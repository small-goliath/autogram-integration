import instaloader
from sqlalchemy.orm import Session
from core.entities import Checker

def delete(db: Session, checker_id: int) -> bool:
    """ID로 체커를 삭제합니다. 삭제되면 True, 그렇지 않으면 False를 반환합니다."""
    checker_to_delete = db.query(Checker).filter(Checker.id == checker_id).first()
    if not checker_to_delete:
        return False
    db.delete(checker_to_delete)
    db.commit()
    return True

def load(db: Session) -> list[Checker]:
    return db.query(Checker).all()

def get(db: Session, username: str) -> Checker | None:
    return db.query(Checker).filter(Checker.username == username).first()

def save(db: Session, username: str) -> Checker:
    new_checker = Checker(username=username)
    db.add(new_checker)
    db.commit()
    db.refresh(new_checker)
    return new_checker
