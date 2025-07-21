import logging
from typing import List
from sqlalchemy.orm import Session
from core.database import consumer_db, group_db
from core.entities import Consumer
from core.exceptions import AlreadyCreatedError, InvalidPropertyError
from core.service.models import ConsumerDetail, GroupDetail

logger = logging.getLogger(__name__)

def get_consumers(db: Session) -> List[ConsumerDetail]:
    consumers: List[Consumer] = consumer_db.load(db)
    return [ConsumerDetail.from_orm(consumer) for consumer in consumers]

def get_consumer(db: Session, username: str) -> ConsumerDetail | None:
    consumer = consumer_db.get(db, username)
    if not consumer:
        return None
    return ConsumerDetail.from_orm(consumer)

def save_consumer(db: Session, username: str, group_id: int) -> None:
    consumer = consumer_db.get(db, username)
    if consumer:
        raise AlreadyCreatedError("이미 등록된 인스타그램 계정입니다.")
    
    instagram_group = group_db.get(db, group_id)
    if not instagram_group:
        raise InvalidPropertyError("유효하지 않은 계정 타입입니다.")

    consumer_db.save(db, username, group_id)
    logger.info(f"소비자 {username}이(가) 성공적으로 저장되었습니다.")