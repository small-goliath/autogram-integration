import logging
import logging.config
import re
import sys
import json
from typing import List
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import random
from batch.util import sleep_to_log
from core.db_transaction import transaction_scope, with_session
from core.service import checkers_service, instagramloader_login_service, verification_service
from batch.notification import Discord
from instaloader import Post
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
        
        # 2. checker 계정으로 로그인 시도
        L = None
        successful_checker = None
        for checker in checkers:
            if not checker.session:
                logger.warning(f"'{checker.username}' checker에 세션이 없습니다. 건너뜁니다.")
                continue
            try:
                L = instagramloader_login_service.login_with_session(checker.username, checker.session)
                if L:
                    logger.info(f"'{checker.username}' 계정으로 로그인 성공.")
                    successful_checker = checker
                    break
            except Exception as e:
                logger.error(f"'{checker.username}' 계정으로 로그인 중 오류 발생: {e}")
                continue
        
        if not L:
            logger.error("모든 checker 계정으로 로그인에 실패했습니다.")
            discord.send_message("활동 검증 checker 계정 로그인 실패.")
            sys.exit(1)

        # 로그인 성공 시 세션 갱신
        try:
            with transaction_scope(db):
                session_data = L.context.get_session()
                session_str = json.dumps(session_data)
                checkers_service.update_checker_session(db, successful_checker.username, session_str)
        except Exception as e:
            logger.error(f"'{successful_checker.username}' 세션 갱신 중 오류 발생: {e}")
            discord.send_message(f"경고: '{successful_checker.username}' 체커 세션 갱신 실패. 다음 실행 시 문제가 발생할 수 있습니다.")

        # 3. 모든 user_action_verification 조회 후 링크별로 그룹화
        verifications: list[VerificationDetail] = verification_service.get_verifications_service(db)
        if not verifications:
            logger.info("검증할 활동이 없습니다.")
            return

        grouped_verifications = defaultdict(list[VerificationDetail])
        for v in verifications:
            grouped_verifications[v.link].append(v)

        logger.info(f"총 {len(verifications)}개의 활동을 {len(grouped_verifications)}개의 링크에 대해 검증합니다.")

        # 4. 링크별로 활동 검증
        for link, user_verifications in grouped_verifications.items():
            try:
                logger.info(f"'{link}' 링크에 대한 {len(user_verifications)}개의 활동을 검증합니다.")
                with transaction_scope(db):
                    shortcode = get_shortcode_from_link(link)
                    post = Post.from_shortcode(L.context, shortcode)

                    likers = {like.username for like in post.get_likes()}
                    sleep_to_log()
                    commenters = {comment.owner.username for comment in post.get_comments()}
                    sleep_to_log(60)

                    for verification in user_verifications:
                        if verification.username in likers and verification.username in commenters:
                            logger.info(f"'{verification.username}'의 좋아요 및 댓글을 확인했습니다. 인증 정보를 삭제합니다.")
                            verification_service.delete_verification(db, verification.id)
                        else:
                            logger.warning(f"'{verification.username}'의 활동을 찾지 못했습니다. (좋아요: {verification.username in likers}, 댓글: {verification.username in commenters})")
            
            except Exception as e:
                logger.error(f"'{link}' 링크 처리 중 오류 발생: {e}")
                discord.send_message(str(e))

        # 5. 검증 결과 요약
        summary = "카카오톡 활동 검증 배치 완료"
        logger.info(summary)
        discord.send_message(summary)

    except Exception as e:
        logger.error(f"배치 실행 중 심각한 오류 발생: {e}", exc_info=True)
        discord.send_message(f"배치 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    verify_actions()
