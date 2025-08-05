import logging
import logging.config
import re
import sys
import os
import instaloader
from typing import List
from collections import defaultdict
from sqlalchemy.orm import Session
from batch.util import sleep_to_log
from core.db_transaction import read_only_transaction_scope, transaction_scope, with_session
from core.service import checkers_service, instagramloader_login_service, instagramloader_session_service, verification_service
from batch.notification import Discord
from instaloader import Post, Profile
from core.service.models import CheckerDetail, VerificationDetail

logging.config.fileConfig('batch/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

def get_shortcode_from_link(link: str) -> str | None:
    """Instagram 링크에서 shortcode를 추출합니다."""
    match = re.search(r"/(p|reel)/([^/]+)", link)
    return match.group(2) if match else None

@with_session
def verify_actions(db: Session):
    logger.info("카카오톡 활동 검증 갱신 배치를 시작합니다.")
    discord = Discord()
    
    try:
        # 1. checker 계정 정보 조회
        checkers: List[CheckerDetail] = checkers_service.get_checkers(db)
        if not checkers:
            logger.error("활동 검증에 사용할 checker 계정이 등록되어 있지 않습니다.")
            discord.send_message("활동 검증에 사용할 checker 계정이 등록되어 있지 않습니다.")
            sys.exit(1)
        
        # 2. 모든 checker 계정 로그인 시도
        logged_in_checkers: List[instaloader.Instaloader] = []
        for checker in checkers:
            try:
                L = instagramloader_login_service.login_with_session_file(checker.username)
                logged_in_checkers.append({'loader': L, 'username': checker.username})
            except Exception as e:
                logger.error(f" checker 계정 '{checker.username}'으로 로그인 실패: {e}")
                continue
        
        if not logged_in_checkers:
            logger.error("모든 checker 계정으로 로그인에 실패했습니다.")
            discord.send_message("활동 검증 checker 계정 로그인 실패.")
            sys.exit(1)

        # 3. 모든 user_action_verification 조회 후 링크별로 그룹화
        verifications: list[VerificationDetail] = verification_service.get_verifications_service(db)
        if not verifications:
            logger.info("검증할 활동이 없습니다.")
            return

        grouped_verifications = defaultdict(list[VerificationDetail])
        for v in verifications:
            grouped_verifications[v.link].append(v)

        logger.info(f"총 {len(verifications)}개의 활동을 {len(grouped_verifications)}개의 링크에 대해 검증합니다.")

        # 4. 링크별로 활동 검증 (예외 발생 시 다른 checker로 재시도)
        num_checkers = len(logged_in_checkers)
        for i, (link, user_verifications) in enumerate(grouped_verifications.items()):
            link_processed = False
            last_exception = None
            
            shortcode = get_shortcode_from_link(link)
            if not shortcode:
                logger.warning(f"'{link}'에서 shortcode를 추출할 수 없습니다.")
                continue

            for j in range(num_checkers):
                checker_index = (i + j) % num_checkers
                checker_info = logged_in_checkers[checker_index]
                L = checker_info['loader']
                checker_username = checker_info['username']
                
                try:
                    logger.info(f"'{checker_username}' 계정으로 '{link}' 링크에 대한 {len(user_verifications)}개의 활동을 검증합니다.")
                    with transaction_scope(db):

                        post = Post.from_shortcode(L.context, shortcode)

                        # likers = {like.username for like in post.get_likes()}
                        sleep_to_log(60)
                        commenters = {comment.owner.username for comment in post.get_comments()}

                        for verification in user_verifications:
                            if verification.username in commenters:
                                logger.info(f"'{verification.username}'의 좋아요 및 댓글을 확인했습니다. 인증 정보를 삭제합니다.")
                                verification_service.delete_verification(db, verification.id)
                            else:
                                logger.warning(f"'{verification.username}'의 활동을 찾지 못했습니다. (좋아요: {verification.username in likers}, 댓글: {verification.username in commenters})")
                    
                    link_processed = True
                    break

                except Exception as e:
                    last_exception = e
                    logger.warning(f"'{checker_username}' 계정으로 '{link}' 링크 처리 중 오류 발생: {e}. 다른 checker로 재시도합니다.")
                    continue
            
            if not link_processed:
                error_message = f"'{link}' 링크 처리 중 모든 checker 계정으로 시도했으나 실패했습니다. 최종 오류: {last_exception}"
                logger.error(error_message)
                discord.send_message(error_message)
                break

        summary = "카카오톡 활동 검증 배치 완료"
        logger.info(summary)
        discord.send_message(summary)

    except Exception as e:
        logger.error(f"배치 실행 중 심각한 오류 발생: {e}", exc_info=True)
        discord.send_message(f"배치 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    verify_actions()
