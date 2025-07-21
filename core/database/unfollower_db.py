from sqlalchemy.orm import Session

from core.entities import UnfollowerCheck

def get_unfollower_check(db: Session, username: str) -> UnfollowerCheck | None:
    """사용자의 최신 언팔로워 확인 기록을 가져옵니다."""
    return db.query(UnfollowerCheck).filter(UnfollowerCheck.username == username).order_by(UnfollowerCheck.id.desc()).first()

def create_or_update_unfollower_check(db: Session, username: str, status: str, message: str = None, unfollowers: list = None) -> UnfollowerCheck:
    """언팔로워 확인 기록을 생성하거나 업데이트합니다."""
    check = db.query(UnfollowerCheck).filter(UnfollowerCheck.username == username).order_by(UnfollowerCheck.id.desc()).first()
    if not check:
        check = UnfollowerCheck(username=username)
        db.add(check)
    
    check.status = status
    check.message = message
    if unfollowers is not None:
        check.unfollowers = unfollowers
    
    db.commit()
    db.refresh(check)
    return check

def delete_unfollower_check(db: Session, username: str):
    """사용자의 모든 언팔로워 확인 기록을 삭제합니다."""
    db.query(UnfollowerCheck).filter(UnfollowerCheck.username == username).delete()
    db.commit()
