import logging
import json
from sqlalchemy.orm import Session
from core.entities import InstagramSession

logger = logging.getLogger(__name__)

def save(db: Session, username: str, settings: dict):
    logger.info(f"{username}의 세션을 저장합니다.")
    session_data = json.dumps(settings).encode('utf-8')

    db.query(InstagramSession).filter(InstagramSession.username == username).delete()

    new_session = InstagramSession(username=username, session_data=session_data)
    db.add(new_session)
    db.commit()
    logger.info(f"{username}의 세션을 성공적으로 저장했습니다.")

def load(db: Session, username: str):
    logger.info(f"{username}의 세션을 로드합니다.")
    session_record = db.query(InstagramSession).filter(InstagramSession.username == username).first()
    if session_record:
        logger.info(f"{username}의 세션을 성공적으로 로드했습니다.")
        return session_record
    logger.warning(f"{username}의 세션을 찾을 수 없습니다.")

def delete(db: Session, username: str):
    logger.info(f"{username}의 세션을 삭제합니다.")
    db.query(InstagramSession).filter(InstagramSession.username == username).delete()
    db.commit()

def get_all_usernames(db: Session) -> list[str]:
    logger.info("저장된 모든 세션의 사용자 이름을 가져옵니다.")
    return [session.username for session in db.query(InstagramSession.username).all()]
