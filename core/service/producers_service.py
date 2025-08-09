import json
import logging
from typing import List
from sqlalchemy.orm import Session
from core.database import producer_db, group_db
from core.entities import Producer
from core.exceptions import AlreadyCreatedError, InvalidPropertyError
from core.service.models import ProducerDetail
from core.service import producer_instagram_service

logger = logging.getLogger(__name__)

def get_producers(db: Session) -> List[ProducerDetail]:
    producers: List[Producer] = producer_db.load(db)
    return [ProducerDetail.from_orm(producer) for producer in producers]

def get_producer(db: Session, username: str) -> ProducerDetail | None:
    producer = producer_db.get(db, username)
    if not producer:
        return None
    return ProducerDetail.from_orm(producer)

def _register_producer(db: Session, username: str, group_id: int, session_string: str) -> ProducerDetail:
    """생산자를 데이터베이스에 저장하는 내부 함수입니다."""
    if get_producer(db, username):
        raise AlreadyCreatedError(f"생산자 {username}이(가) 이미 존재합니다.")

    group = group_db.get(db, group_id)
    if not group:
        raise InvalidPropertyError(f"ID가 {group_id}인 그룹을 찾을 수 없습니다.")

    producer = producer_db.save(db, username, group_id, session_string)
    return ProducerDetail.from_orm(producer)


def update_producer_session(db: Session, username: str, settings: dict):
    """생산자 세션을 데이터베이스에 업데이트합니다."""
    logger.info(f"'{username}' 계정의 세션을 갱신합니다.")
    session_string = json.dumps(settings).encode('utf-8')
    producer = producer_db.update_session(db, username, session_string)
    if not producer:
        logger.warning(f"'{username}' 계정의 세션을 갱신하는데 실패했습니다. DB에서 사용자를 찾을 수 없습니다.")
    else:
        logger.info(f"'{username}' 계정의 세션을 갱신했습니다.")


def login_and_register_producer(db: Session, username: str, password: str, group_id: int) -> ProducerDetail:
    group = group_db.get(db, group_id)
    if not group:
        raise InvalidPropertyError(f"ID가 {group_id}인 그룹을 찾을 수 없습니다.")

    if get_producer(db, username):
        raise AlreadyCreatedError(f"생산자 {username}이(가) 이미 존재합니다.")

    session_string = producer_instagram_service.login_producer(username, password)

    logger.info(f"{username}의 로그인이 성공했습니다. 생산자로 등록합니다.")
    producer = _register_producer(db, username, group_id, session_string)
    return producer

def complete_2fa_and_register_producer(db: Session, username: str, verification_code: str, group_id: int) -> ProducerDetail:
    """
    2FA 완료 및 등록 프로세스를 조정합니다.
    1. 2FA 로그인을 완료합니다.
    2. 생산자를 등록합니다.

    InstagramLoginError, AlreadyCreatedError, InvalidPropertyError를 발생시킵니다.
    """
    # 실패 시 로그인 오류를 발생시킵니다.
    session_string = producer_instagram_service.complete_2fa_producer(username, verification_code)

    logger.info(f"{username}의 2FA 로그인이 성공했습니다. 생산자로 등록합니다.")
    producer = _register_producer(db, username, group_id, session_string)
    return producer
