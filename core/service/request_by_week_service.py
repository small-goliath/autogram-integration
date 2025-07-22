import logging
from sqlalchemy.orm import Session
from core.database import request_by_week_db
from core.entities import RequestByWeek
from batch.models import KakaoTalk

logger = logging.getLogger(__name__)

def update_request_by_week(db: Session, parsed_links: list[KakaoTalk]):
    """
    주간 요청 테이블을 업데이트합니다.
    기존 데이터를 모두 삭제하고 새로운 데이터로 교체합니다.
    """
    logger.info("주간 요청 테이블 업데이트를 시작합니다.")
    try:
        request_by_week_db.clear_request_by_week(db)
        
        requests_to_add = []
        inserted = set()
        for item in parsed_links:
            if (item.username, item.link) not in inserted:
                requests_to_add.append(RequestByWeek(username=item.username, link=item.link))
                inserted.add((item.username, item.link))
        
        request_by_week_db.save_request_by_week(db, requests_to_add)
        logger.info("주간 요청 테이블 업데이트를 완료했습니다.")
    except Exception as e:
        logger.error(f"주간 요청 테이블 업데이트 중 오류 발생: {e}", exc_info=True)
        raise

def get_all_requests(db: Session) -> list[RequestByWeek]:
    """모든 주간 요청을 조회합니다."""
    logger.info("모든 주간 요청 조회를 시작합니다.")
    try:
        requests = request_by_week_db.get_all_requests(db)
        logger.info(f"{len(requests)}개의 주간 요청을 반환합니다.")
        return requests
    except Exception as e:
        logger.error(f"모든 주간 요청 조회 중 오류 발생: {e}", exc_info=True)
        raise
