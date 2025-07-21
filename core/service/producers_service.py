import logging
from typing import List
from sqlalchemy.orm import Session
from core.database import producer_db, group_db
from core.entities import Producer
from core.exceptions import AlreadyCreatedError, InvalidPropertyError, Instagram2FAError, InstagramLoginError
from core.service.models import ProducerDetail
from core.service import instagram_login_service

logger = logging.getLogger(__name__)

def get_producers(db: Session) -> List[ProducerDetail]:
    producers: List[Producer] = producer_db.load(db)
    return [ProducerDetail.from_orm(producer) for producer in producers]

def get_producer(db: Session, username: str) -> ProducerDetail | None:
    producer = producer_db.get(db, username)
    if not producer:
        return None
    return ProducerDetail.from_orm(producer)

def _register_producer(db: Session, username: str, group_id: int) -> ProducerDetail:
    """생산자를 데이터베이스에 저장하는 내부 함수입니다."""
    if get_producer(db, username):
        raise AlreadyCreatedError(f"생산자 {username}이(가) 이미 존재합니다.")

    group = group_db.get(db, group_id)
    if not group:
        raise InvalidPropertyError(f"ID가 {group_id}인 그룹을 찾을 수 없습니다.")

    producer = producer_db.save(db, username, group_id)
    return ProducerDetail.from_orm(producer)

def login_and_register_producer(db: Session, username: str, password: str, group_id: int) -> ProducerDetail:
    """
    로그인 및 등록 프로세스를 조정합니다.
    1. 그룹이 유효한지 확인합니다.
    2. 생산자가 이미 존재하는지 확인합니다.
    3. 인스타그램에 로그인합니다.
    4. 생산자를 등록합니다.
    
    Instagram2FAError, InstagramLoginError, AlreadyCreatedError, InvalidPropertyError를 발생시킵니다.
    """
    group = group_db.get(db, group_id)
    if not group:
        raise InvalidPropertyError(f"ID가 {group_id}인 그룹을 찾을 수 없습니다.")

    if get_producer(db, username):
        raise AlreadyCreatedError(f"생산자 {username}이(가) 이미 존재합니다.")

    # API 계층에서 포착될 2FA 또는 로그인 오류를 발생시킵니다.
    instagram_login_service.login(db, username, password)
    
    logger.info(f"{username}의 로그인이 성공했습니다. 생산자로 등록합니다.")
    producer = _register_producer(db, username, group_id)
    return producer

def complete_2fa_and_register_producer(db: Session, username: str, verification_code: str, group_id: int) -> ProducerDetail:
    """
    2FA 완료 및 등록 프로세스를 조정합니다.
    1. 2FA 로그인을 완료합니다.
    2. 생산자를 등록합니다.

    InstagramLoginError, AlreadyCreatedError, InvalidPropertyError를 발생시킵니다.
    """
    # 실패 시 로그인 오류를 발생시킵니다.
    instagram_login_service.login_2fa(db, username, verification_code)

    logger.info(f"{username}의 2FA 로그인이 성공했습니다. 생산자로 등록합니다.")
    producer = _register_producer(db, username, group_id)
    return producer
