from sqlalchemy.orm import Session

from core.entities import Producer

def get(db: Session, username: str) -> Producer | None:
    return db.query(Producer).filter(Producer.username == username).first()

def load(db: Session) -> list[Producer]:
    return db.query(Producer).all()

def save(db: Session, username:str, group_id: int, session_string: str) -> Producer:
    db_producer = Producer(username=username, group_id=group_id, enabled=False, session=session_string)
    db.add(db_producer)
    db.commit()
    db.refresh(db_producer)
    return db_producer