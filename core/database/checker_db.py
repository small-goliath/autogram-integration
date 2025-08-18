from sqlalchemy.orm import Session
from core.entities import Checker

def delete(db: Session, checker_id: int) -> bool:
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

def save(db: Session, username: str, session: str) -> Checker:
    new_checker = Checker(username=username, session=session)
    db.add(new_checker)
    db.commit()
    db.refresh(new_checker)
    return new_checker

def update_session(db: Session, username: str, session_string: str) -> Checker | None:
    db_checker = db.query(Checker).filter(Checker.username == username).first()
    if db_checker:
        db_checker.session = session_string
        db.add(db_checker)
        db.commit()
        db.refresh(db_checker)
    return db_checker

def update_session(db: Session, username: str, password: str) -> Checker | None:
    db_checker = db.query(Checker).filter(Checker.username == username).first()
    if db_checker:
        db_checker.pwd = password
        db.add(db_checker)
        db.commit()
        db.refresh(db_checker)
    return db_checker