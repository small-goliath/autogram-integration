import json
import logging
from typing import List
from sqlalchemy.orm import Session
from core.database import checker_db
from core.entities import Checker
from core.exceptions import AlreadyCreatedError, InstagramLoginError
from core.service import instagram_login_service, instagram_session_service
from core.service.models import CheckerDetail

logger = logging.getLogger(__name__)

def get_checkers(db: Session) -> List[CheckerDetail]:
    checkers: List[Checker] = checker_db.load(db)
    return [CheckerDetail.from_orm(checker) for checker in checkers]

def delete_checker(db: Session, checker_id: int) -> bool:
    return checker_db.delete(db, checker_id)

def register_checker(db: Session, username: str, password: str) -> CheckerDetail:
    if checker_db.get(db, username):
        raise AlreadyCreatedError(f"체커 계정 {username}이(가) 이미 존재합니다.")

    instagram_login_service.login(db, username, password)
    session_string = instagram_session_service.get_session_string(db, username)
    
    if not session_string:
        raise InstagramLoginError("세션 문자열을 가져오는 데 실패했습니다.")

    new_checker = checker_db.save(db, username, session_string)
    logger.info(f"체커 계정 {username}을(를) 성공적으로 등록하고 세션을 저장했습니다.")
    
    return CheckerDetail.from_orm(new_checker)

def complete_2fa_and_register_checker(db: Session, username: str, verification_code: str) -> CheckerDetail:
    if checker_db.get(db, username):
        raise AlreadyCreatedError(f"체커 계정 {username}이(가) 이미 존재합니다.")

    instagram_login_service.login_2fa(db, username, verification_code)
    session_string = instagram_session_service.get_session_string(db, username)

    if not session_string:
        raise InstagramLoginError("2FA 후 세션 문자열을 가져오는 데 실패했습니다.")

    new_checker = checker_db.save(db, username, session_string)
    logger.info(f"체커 계정 {username}의 2FA를 완료하고 세션을 저장했습니다.")
    
    return CheckerDetail.from_orm(new_checker)

def get_checker_by_username(db: Session, username: str) -> CheckerDetail | None:
    checker = checker_db.get(db, username)
    if checker:
        return CheckerDetail.from_orm(checker)
    return None

def update_session(db: Session, username: str, settings: dict):
    """세션을 데이터베이스에 업데이트합니다."""
    logger.info(f"'{username}' 계정의 세션을 갱신합니다.")
    session_string = json.dumps(settings).encode('utf-8')
    producer = checker_db.update_session(db, username, session_string)
    if not producer:
        logger.warning(f"'{username}' 계정의 세션을 갱신하는데 실패했습니다. DB에서 사용자를 찾을 수 없습니다.")
    else:
        logger.info(f"'{username}' 계정의 세션을 갱신했습니다.")