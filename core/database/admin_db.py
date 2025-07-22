from sqlalchemy.orm import Session
from core.entities import Admin

def get_admin_by_credentials(db: Session, username: str, api_key: str) -> Admin | None:
    """
    주어진 사용자 이름과 API 키로 관리자를 조회합니다.
    """
    return db.query(Admin).filter(Admin.username == username, Admin.ap_key == api_key).first()
