import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from api.routes.payloads import MessageResponse, UnfollowerCheckStatusResponse
from core.db_transaction import get_db
from core.service import unfollower_service
from core.exceptions import UserNotPermittedError

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/{username}", response_model=MessageResponse)
async def start_unfollow_check(
    username: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    logger.info(f"[{username}] 언팔로워 확인 요청 수신")
    try:
        return unfollower_service.start_unfollow_check_service(db, username, background_tasks)
    except UserNotPermittedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"[{username}] 언팔로워 확인 시작 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="내부 서버 오류가 발생했습니다.")


@router.get("/{username}", response_model=UnfollowerCheckStatusResponse)
async def get_unfollow_check_status(username: str, db: Session = Depends(get_db)):
    try:
        return unfollower_service.get_unfollow_check_status_service(db, username)
    except Exception as e:
        logger.error(f"[{username}] 언팔로워 확인 상태 조회 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="내부 서버 오류가 발생했습니다.")

