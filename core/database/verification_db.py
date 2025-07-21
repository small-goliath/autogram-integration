from sqlalchemy import and_
from sqlalchemy.orm import Session

from core.entities import UserActionVerification


def get_all_verifications(db: Session):
    """모든 사용자 활동 인증을 가져옵니다."""
    return db.query(UserActionVerification).all()


def save_verification_if_not_exists(session: Session, verification: UserActionVerification) -> bool:
    """검증 결과가 존재하지 않으면 데이터베이스에 저장합니다."""
    exists = session.query(UserActionVerification).filter(
        and_(
            UserActionVerification.username == verification.username,
            UserActionVerification.link == verification.link,
        )
    ).first()
    if not exists:
        session.add(verification)
        return True
    return False


def delete_verification_by_id(db: Session, verification_id: int):
    """ID로 사용자 활동 인증을 삭제합니다."""
    verification = db.query(UserActionVerification).filter(UserActionVerification.id == verification_id).first()
    if verification:
        db.delete(verification)
        return True
    return False
