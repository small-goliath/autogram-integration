import logging
from sqlalchemy.orm import Session
from core.entities import RequestByWeek

logger = logging.getLogger(__name__)

def clear_request_by_week(db: Session):
    """request_by_week 테이블의 모든 데이터를 삭제합니다."""
    logger.info("request_by_week 테이블을 비웁니다.")
    db.query(RequestByWeek).delete()

def save_request_by_week(db: Session, requests: list[RequestByWeek]):
    """파싱된 카카오톡 링크를 request_by_week 테이블에 저장합니다."""
    logger.info(f"{len(requests)}개의 요청을 request_by_week 테이블에 저장합니다.")
    db.add_all(requests)

def get_all_requests(db: Session) -> list[RequestByWeek]:
    """request_by_week 테이블의 모든 데이터를 조회합니다."""
    logger.info("request_by_week 테이블의 모든 데이터를 조회합니다.")
    return db.query(RequestByWeek).all()
