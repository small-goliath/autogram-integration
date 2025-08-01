import logging
import logging.config
import re
import sys
from typing import List

import instaloader
from dotenv import load_dotenv

from batch.kakaotalk_parsing import parsing
from batch.notification import Discord
from batch.util import sleep_to_log
from core.db_transaction import with_session
from core.entities import UserActionVerification
from core.service import (checkers_service, instagramloader_login_service, users_service, verification_service)
from core.service.models import CheckerDetail, KakaoTalk, UserDetail

load_dotenv()
logging.config.fileConfig('batch/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

def get_shortcode_from_link(link: str) -> str | None:
    """Instagram 링크에서 shortcode를 추출합니다."""
    match = re.search(r"/(p|reel)/([^/]+)", link)
    return match.group(2) if match else None

@with_session
def verify_actions(db):
    """
    카카오톡으로 공유한 인스타그램 게시물에 대해
    sns_raise_user들이 좋아요와 댓글을 남겼는지 확인하고,
    그렇지 않은 경우 user_action_verification 테이블에 기록합니다.
    """
    logger.info("카카오톡 활동 검증 배치를 시작합니다.")
    discord = Discord()

    try:
        # 1. 카카오톡 파싱으로 게시물 목록 가져오기
        kakaotalk_posts: list[KakaoTalk] = parsing()
        if not kakaotalk_posts:
            logger.info("검증할 게시물이 없습니다.")
            discord.send_message("카카오톡 활동 검증: 검증할 게시물이 없습니다.")
            return

        # 2. checker 계정 정보 조회
        checkers: List[CheckerDetail] = checkers_service.get_checkers(db)
        if not checkers:
            logger.error("활동 검증에 사용할 checker 계정이 등록되어 있지 않습니다.")
            discord.send_message("활동 검증에 사용할 checker 계정이 등록되어 있지 않습니다.")
            sys.exit(1)

        # 3. checker 계정으로 로그인 시도
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

        # 4. 모든 sns_raise_user 조회
        all_users: List[UserDetail] = users_service.get_users(db)
        if not all_users:
            logger.warning("활동을 검증할 sns_raise_user가 없습니다.")
            return

        added_verifications = set()
        saved_count = 0

        # 5. 좋아요 및 댓글 검증
        num_checkers = len(logged_in_checkers)
        logger.info(f"총 {len(kakaotalk_posts)}개의 게시글을 검증합니다.")
        for i, post_info in enumerate(kakaotalk_posts):
            link_processed = False
            last_exception = None

            shortcode = get_shortcode_from_link(post_info.link)
            if not shortcode:
                logger.warning(f"링크에서 shortcode를 추출할 수 없습니다: {post_info.link}")
                continue

            for j in range(num_checkers):
                checker_index = (i + j) % num_checkers
                checker_info = logged_in_checkers[checker_index]
                L = checker_info['loader']
                checker_username = checker_info['username']

                try:
                    logger.info(f"'{checker_username}'으로 {post_info.username}의 게시물 검증 중: {post_info.link}")
                    post = instaloader.Post.from_shortcode(L.context, shortcode)

                    likers = {like.username for like in post.get_likes()}
                    sleep_to_log()
                    commenters = {comment.owner.username for comment in post.get_comments()}
                    sleep_to_log(60)

                    for user in all_users:
                        if user.username == post.owner_username:
                            continue

                        is_liked = user.username in likers
                        is_commented = user.username in commenters

                        if not is_liked or not is_commented:
                            verification_key = (user.username, post_info.link)
                            if verification_key not in added_verifications:
                                v = UserActionVerification(
                                    username=user.username,
                                    link=post_info.link
                                )
                                if verification_service.save_verification(db, v):
                                    logger.info(f"새로운 미완료 활동을 기록했습니다: username={v.username}, link={v.link}")
                                    saved_count += 1
                                added_verifications.add(verification_key)

                    link_processed = True
                    break

                except Exception as e:
                    last_exception = e
                    logger.error(f"'{checker_username}'으로 게시물({shortcode}) 처리 중 오류 발생: {e}")
                    discord.send_message(f"'{checker_username}'으로 게시물({shortcode}) 처리 중 오류 발생: {e}")
                    continue

            if not link_processed:
                error_message = f"신규 '{post_info.link}' 링크 처리 중 모든 checker 계정으로 시도했으나 실패했습니다. 최종 오류: {last_exception}"
                logger.error(error_message)
                discord.send_message(error_message)
                break

        if saved_count > 0:
            logger.info(f"총 {saved_count}개의 새로운 미완료 활동을 기록했습니다.")
        else:
            logger.info("모든 사용자가 모든 활동을 완료했습니다. 새로운 미완료 활동이 없습니다.")

        logger.info("카카오톡 활동 검증 배치를 성공적으로 완료했습니다.")
        discord.send_message("카카오톡 활동 검증 배치를 성공적으로 완료했습니다.")

    except Exception as e:
        logger.error(f"배치 실행 중 심각한 오류 발생: {e}", exc_info=True)
        discord.send_message(f"배치 실행 중 심각한 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    verify_actions()

