import logging
from typing import List
from fastapi import APIRouter, HTTPException, Body, Depends
from sqlalchemy.orm import Session

from backend.routes.payloads import (
    ProducerLoginRequest,
    ProducerVerificationCodeRequest,
    ProducersResponse,
    MessageResponse,
)
from core.db_transaction import get_db
from core.exceptions import (
    Instagram2FAError,
    InstagramLoginError,
    AlreadyCreatedError,
    InvalidPropertyError,
)
from core.service import producers_service
from core.service.models import ProducerDetail

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/login", response_model=MessageResponse)
async def producer_login(
    request: ProducerLoginRequest = Body(...),
    db: Session = Depends(get_db)
):
    try:
        producers_service.login_and_register_producer(
            db, request.username, request.password, request.group_id
        )
        return MessageResponse(
            message=f"성공적으로 로그인하고 Producer를 등록했습니다: {request.username}"
        )
    except Instagram2FAError:
        logger.warning(f"{request.username}에 2FA가 필요합니다")
        return MessageResponse(message="2FA 코드가 필요합니다.", two_factor_required=True)
    except (InstagramLoginError, AlreadyCreatedError, InvalidPropertyError) as e:
        logger.error(f"Producer {request.username} 로그인 실패: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Producer 로그인 중 예상치 못한 오류 발생 {request.username}: {e}")
        raise HTTPException(status_code=500, detail="예상치 못한 오류가 발생했습니다.")

@router.post("/login/2fa", response_model=MessageResponse)
async def producer_login_2fa(
    request: ProducerVerificationCodeRequest = Body(...),
    db: Session = Depends(get_db)
):
    try:
        producers_service.complete_2fa_and_register_producer(
            db, request.username, request.verification_code, request.group_id
        )
        return MessageResponse(
            message=f"2FA를 성공적으로 완료하고 Producer를 등록했습니다: {request.username}"
        )
    except (InstagramLoginError, AlreadyCreatedError, InvalidPropertyError) as e:
        logger.error(f"Producer {request.username}의 2FA 완료 실패: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Producer 2FA 중 예상치 못한 오류 발생 {request.username}: {e}")
        raise HTTPException(status_code=500, detail="예상치 못한 오류가 발생했습니다.")

@router.get("", response_model=ProducersResponse)
def search_producers(db: Session = Depends(get_db)):
    producers: List[ProducerDetail] = producers_service.get_producers(db)
    return ProducersResponse(count=len(producers), details=producers)
