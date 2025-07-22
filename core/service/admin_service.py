from sqlalchemy.orm import Session
from core.database import admin_db

def verify_admin_credentials(db: Session, username: str, api_key: str) -> bool:
    """
    관리자 자격 증명을 확인합니다.
    """
    admin = admin_db.get_admin_by_credentials(db, username, api_key)
    return admin is not None
