from sqlalchemy.orm import Session

from core.entities import Consumer

def get(db: Session, username: str):
    return db.query(Consumer).filter(Consumer.username == username).first()

def load(db: Session):
    return db.query(Consumer).all()

def save(db: Session, username: str, group_id: int):
    db_consumer = Consumer(username=username, group_id=group_id, enabled=False)
    db.add(db_consumer)