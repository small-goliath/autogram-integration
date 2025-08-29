import logging
import logging.config
import sys
from typing import List
from collections import defaultdict
from batch import util
from batch.action_support import Action
from batch.util import sleep_to_log
from core.db_transaction import read_only_transactional, transactional
from core.service import checkers_service, instagrapi_login_service, verification_service
from batch.notification import Discord
from core.service.models import CheckerDetail, VerificationDetail

logging.config.fileConfig('batch/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

def verify_actions():
    logger.info("카카오톡 활동 검증 갱신 배치를 시작합니다.")
    discord = Discord()
    
    try:
        with read_only_transactional() as db:
            checkers: List[CheckerDetail] = checkers_service.get_checkers(db)
            if not checkers:
                logger.error("활동 검증에 사용할 checker 계정이 등록되어 있지 않습니다.")
                discord.send_message("활동 검증에 사용할 checker 계정이 등록되어 있지 않습니다.")
                sys.exit(1)
        
        logged_in_checkers: List[dict[str, Action | str]] = []
        for checker in checkers:
            try:
                cl = instagrapi_login_service.login_with_session(checker.username, checker.session)
                action = Action(cl=cl)
                logged_in_checkers.append({'action': action, 'username': checker.username})
            except Exception as e:
                logger.error(f" checker 계정 '{checker.username}'으로 로그인 실패: {e}")
                continue
        
        if not logged_in_checkers:
            logger.error("모든 checker 계정으로 로그인에 실패했습니다.")
            discord.send_message("활동 검증 checker 계정 로그인 실패.")
            sys.exit(1)
        with read_only_transactional() as db:
            verifications: list[VerificationDetail] = verification_service.get_verifications_service(db)
            if not verifications:
                logger.info("검증할 활동이 없습니다.")
                return

        grouped_verifications = defaultdict(list)
        for v in verifications:
            grouped_verifications[v.link].append(v)

        logger.info(f"총 {len(verifications)}개의 활동을 {len(grouped_verifications)}개의 링크에 대해 검증합니다.")

        num_checkers = len(logged_in_checkers)
        for i, (link, user_verifications) in enumerate(grouped_verifications.items()):
            link_processed = False
            last_exception = None
            
            shortcode = util.get_shortcode_from_link(link)
            if not shortcode:
                continue

            for j in range(num_checkers):
                checker_index = (i + j) % num_checkers
                checker_info = logged_in_checkers[checker_index]
                action = checker_info['action']
                checker_username = checker_info['username']
                
                try:
                    logger.info(f"'{checker_username}' 계정으로 '{link}' 링크에 대한 {len(user_verifications)}개의 활동을 검증합니다.")
                    with transactional() as db:
                        media_pk = action.media_pk(shortcode)
                        commenters = action.get_commenters(media_pk)

                        for verification in user_verifications:
                            if verification.username in commenters:
                                logger.info(f"'{verification.username}'의 댓글을 확인했습니다. 업데이트합니다.")
                                verification_service.delete_verification(db, verification.id)
                    
                    link_processed = True
                    break

                except Exception as e:
                    logger.warning(f"'{checker_username}' 계정으로 '{link}' 링크 처리 중 오류 발생: {e}. 다른 checker로 재시도합니다.")
                    if "Media not found or unavailable" in str(e):
                        break
                    continue
                finally:
                    sleep_to_log()
            
            if not link_processed:
                error_message = f"'{link}' 링크 처리 중 모든 checker 계정으로 시도했으나 실패했습니다. 최종 오류: {last_exception}"
                logger.error(error_message)
                discord.send_message(error_message)
                continue

        for logged_in_checker in logged_in_checkers:
            with transactional() as db:
                try:
                    action: Action = logged_in_checker["action"]
                    action.checker_update_session(db)
                except Exception as e:
                    continue

        summary = "카카오톡 활동 검증 배치 완료"
        logger.info(summary)
        discord.send_message(summary)

    except Exception as e:
        logger.error(f"배치 실행 중 심각한 오류 발생: {e}")
        discord.send_message(f"배치 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    verify_actions()
