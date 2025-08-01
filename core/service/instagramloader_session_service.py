import logging
import pickle
from instaloader import instaloader
from sqlalchemy.orm import Session
from core.database import instagram_session_db
from core.entities import InstagramSession
from core.Instagram import InstagramLoader

logger = logging.getLogger(__name__)

def get_session_context(db: Session, username: str) -> instaloader.InstaloaderContext | None:
    """
    데이터베이스에서 사용자의 세션 컨텍스트를 로드합니다.
    """
    session_record: InstagramSession = instagram_session_db.load(db, username)
    if session_record:
        try:
            return pickle.loads(session_record.session_data)
        except Exception as e:
            logger.error(f"{username}의 세션을 로드하는 중 오류 발생: {e}", exc_info=True)
            instagram_session_db.delete(db, username)
    return None

def save_session(db: Session, username: str, L_context: instaloader.InstaloaderContext):
    """
    사용자의 세션 컨텍스트를 데이터베이스에 저장합니다.
    """
    instagram_session_db.save(db, username, L_context)

def delete_session(db: Session, username: str):
    """
    데이터베이스에서 사용자의 세션을 삭제합니다.
    """
    instagram_session_db.delete(db, username)

def has_session(db: Session, username: str) -> bool:
    """
    사용자가 유효한 세션을 가지고 있는지 확인합니다.
    """
    return get_session_context(db, username) is not None

def get_session_string(db: Session, username: str) -> str | None:
    """
    저장된 세션 컨텍스트에서 세션 문자열을 가져옵니다.
    """
    logger.info(f"{username}의 세션 문자열을 가져옵니다.")
    context = get_session_context(db, username)
    if context:
        try:
            return InstagramLoader.context_to_string(context)
        except Exception as e:
            logger.error(f"{username}의 세션 문자열을 가져오는 중 오류 발생: {e}", exc_info=True)
    logger.warning(f"{username}의 세션 문자열을 가져올 수 없습니다.")
    return None

def get_all_session_usernames(db: Session) -> list[str]:
    """
    저장된 세션이 있는 모든 사용자 이름을 가져옵니다.
    """
    return instagram_session_db.get_all_usernames(db)

def load_session_context(db: Session, username: str):
    """
    세션 컨텍스트를 로드합니다. get_session_context의 별칭입니다.
    """
    return get_session_context(db, username)