import logging
from sqlalchemy.orm import Session

from core.entities import SnsRaiseUser

logger = logging.getLogger(__name__)

def get_by_username(db: Session, username: str) -> SnsRaiseUser | None:
    logger.info(f"사용자 이름으로 SNS Raise 사용자 찾기: {username}")
    return db.query(SnsRaiseUser).filter(SnsRaiseUser.username == username).first()

def load(db: Session) -> list[SnsRaiseUser]:
    logger.info("SNS 키우기 사용자 목록을 조회합니다.")
    users = db.query(SnsRaiseUser).all()
    return users
    
def save(db: Session, username: str) -> SnsRaiseUser:
    logger.info(f"SNS 키우기 사용자 {username}을 추가합니다.")
    new_user = SnsRaiseUser(username=username)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def delete(db: Session, username: str) -> bool:
    logger.info(f"SNS 키우기 사용자 {username}을 삭제합니다.")
    user_to_delete = db.query(SnsRaiseUser).filter(SnsRaiseUser.username == username).first()
    if not user_to_delete:
        return False
    db.delete(user_to_delete)
    db.commit()
    return True
