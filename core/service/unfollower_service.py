import logging
import json
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, UserNotFound, PrivateAccount

from core.db_transaction import get_db_session_context
from core.database import unfollower_db, user_db, instagram_session_db
from core.exceptions import UserNotPermittedError
from core.service.models import Message, UnfollowerCheckStatus

logger = logging.getLogger(__name__)

def _run_unfollow_check_logic(username: str):
    """
    백그라운드 작업으로 실행되며 자체 DB 세션을 관리
    """
    logger.info(f"[{username}] 언팔로워 확인 백그라운드 작업을 시작합니다.")
    cl = Client()

    def set_status(db_session, status, message=None, unfollowers=None):
        unfollower_db.create_or_update_unfollower_check(db_session, username, status, message, unfollowers)

    try:
        with get_db_session_context() as db:
            set_status(db, "processing", message="인스타그램 세션을 불러오는 중...")
            
            session_record = instagram_session_db.load(db, username)
            if not session_record:
                logger.warning(f"[{username}] 로그인 세션을 찾을 수 없습니다. 중단합니다.")
                set_status(db, "error", message="로그인 세션을 찾을 수 없습니다. 다시 로그인해주세요.")
                return

            try:
                settings = json.loads(session_record.session_data.decode('utf-8'))
                cl.set_settings(settings)
                cl.login_by_sessionid(cl.sessionid)
            except Exception:
                logger.error(f"[{username}] 세션 로딩 오류.")
                set_status(db, "error", message="세션이 만료되었거나 유효하지 않습니다. 다시 로그인해주세요.")
                instagram_session_db.delete(db, username)
                return

            set_status(db, "processing", message=f"'{username}'의 프로필 정보를 가져오는 중...")
        
        user_id = cl.user_id_from_username(username)
        
        with get_db_session_context() as db:
            set_status(db, "processing", message="팔로워 목록을 가져오는 중...")
        followers = cl.user_followers(user_id)
        followers_set = set(followers.keys())
        
        with get_db_session_context() as db:
            logger.info(f"[{username}] {len(followers_set)}명의 팔로워를 찾았습니다.")
            set_status(db, "processing", message="팔로잉 목록을 가져오는 중...")
        following = cl.user_following(user_id)
        
        with get_db_session_context() as db:
            logger.info(f"[{username}] {len(following)}명을 팔로잉하고 있습니다.")
            unfollowers_data = [
                {"username": user.username, "profile_pic_url": str(user.profile_pic_url)}
                for user_id, user in following.items()
                if user_id not in followers_set
            ]
            logger.info(f"[{username}] {len(unfollowers_data)}명의 언팔로워를 찾았습니다.")
            
            unfollowers_data_sorted = sorted(unfollowers_data, key=lambda x: x['username'])
            
            set_status(db, "completed", unfollowers=unfollowers_data_sorted, message="완료되었습니다.")
            logger.info(f"[{username}] 언팔로워 확인이 완료되었습니다.")

    except UserNotFound:
        logger.error(f"[{username}] 프로필을 찾을 수 없습니다.")
        with get_db_session_context() as db:
            set_status(db, "error", message=f"인스타그램 프로필 '{username}'을(를) 찾을 수 없습니다.")
    except LoginRequired:
        logger.error(f"[{username}] 프로필을 보려면 로그인이 필요합니다.")
        with get_db_session_context() as db:
            set_status(db, "error", message=f"'{username}' 프로필을 보려면 로그인이 필요합니다. 다시 로그인해주세요.")
    except PrivateAccount:
        logger.error(f"[{username}] 비공개 계정입니다.")
        with get_db_session_context() as db:
            set_status(db, "error", message=f"'{username}'님은 비공개 계정이라 확인할 수 없습니다.")
    except Exception as e:
        logger.error(f"[{username}] 알 수 없는 오류가 발생했습니다: {e}")
        with get_db_session_context() as db:
            set_status(db, "error", message=f"알 수 없는 오류가 발생했습니다: {str(e)}")


def start_unfollow_check_service(db: Session, username: str, background_tasks: BackgroundTasks) -> Message:
    logger.info(f"[{username}] 언팔로워 확인 시작 요청을 받았습니다.")
    
    sns_raise_user = user_db.get_by_username(db, username)
    if not sns_raise_user:
        logger.warning(f"[{username}] 권한 없는 사용자가 언팔로워 확인을 시작하려고 시도했습니다.")
        raise UserNotPermittedError("언팔로워 검색은 SNS 키우기 품앗이 유저만 이용 가능합니다.")

    logger.info(f"[{username}] 이전 확인 기록을 삭제합니다.")
    unfollower_db.delete_unfollower_check(db, username)
    unfollower_db.create_or_update_unfollower_check(db, username, "processing", message="언팔로워 확인 작업을 시작합니다...")

    logger.info(f"[{username}] 언팔로워 확인을 백그라운드 작업으로 시작합니다.")
    background_tasks.add_task(_run_unfollow_check_logic, username)
    
    return Message(message="언팔로워 확인 작업을 시작했습니다. 잠시 후 결과가 표시됩니다.")


def get_unfollow_check_status_service(db: Session, username:str) -> UnfollowerCheckStatus:
    check = unfollower_db.get_unfollower_check(db, username)
    if not check:
        return UnfollowerCheckStatus(status="idle")
    
    status = UnfollowerCheckStatus.from_orm(check)
    if check.updated_at or check.created_at:
        status.last_updated = (check.updated_at or check.created_at).timestamp()
    return status
