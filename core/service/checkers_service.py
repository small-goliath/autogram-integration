import logging
from typing import List
from sqlalchemy.orm import Session
from core.database import checker_db
from core.entities import Checker
from core.exceptions import AlreadyCreatedError, NotFoundError
from core.service import instagramloader_session_service
from core.service.models import CheckerDetail

logger = logging.getLogger(__name__)

def get_checkers(db: Session) -> List[CheckerDetail]:
    checkers: List[Checker] = checker_db.load(db)
    return [CheckerDetail.from_orm(checker) for checker in checkers]

def delete_checker(db: Session, checker_id: int) -> bool:
    return checker_db.delete(db, checker_id)

def register_checker(db: Session, username: str) -> CheckerDetail:
    """
    이미 인증된 세션을 사용하여 계정을 체커로 등록합니다.
    """
    if checker_db.get(db, username):
        raise AlreadyCreatedError(f"체커 계정 {username}이(가) 이미 존재합니다.")

    session_str = instagramloader_session_service.get_session_string(db, username)
    
    if not session_str:
        raise NotFoundError(f"{username}에 대한 활성 세션을 찾을 수 없습니다. 먼저 로그인해야 합니다.")

    new_checker = checker_db.save(db, username, session_str)
    logger.info(f"체커 계정 {username}을(를) 성공적으로 등록했습니다.")
    
    return CheckerDetail.from_orm(new_checker)