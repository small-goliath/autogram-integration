import logging
from typing import List
from fastapi import APIRouter, HTTPException, Response, Depends, Body
from sqlalchemy.orm import Session

from backend.routes.admin.auth import verify_admin
from backend.routes.payloads import (
    CheckerDetailResponse,
    RegisterCheckerRequest,
    InstagramVerificationCodeRequest,
    MessageResponse,
)
from core.db_transaction import get_db
from core.exceptions import AlreadyCreatedError, Instagram2FAError, InstagramLoginError
from core.service import checkers_service

router = APIRouter(dependencies=[Depends(verify_admin)])
logger = logging.getLogger(__name__)

@router.get("", response_model=List[CheckerDetailResponse])
def get_all_checkers(db: Session = Depends(get_db)):
    checker_details = checkers_service.get_checkers(db)
    return checker_details

@router.delete("/{checker_id}", status_code=204)
def remove_checker(checker_id: int, db: Session = Depends(get_db)):
    was_deleted = checkers_service.delete_checker(db, checker_id)
    if not was_deleted:
        raise HTTPException(status_code=404, detail=f"ID가 {checker_id}인 체커를 찾을 수 없습니다.")
    return Response(status_code=204)

@router.post("/login", response_model=MessageResponse)
def register_checker(
    account: RegisterCheckerRequest = Body(...),
    db: Session = Depends(get_db)
):
    try:
        checkers_service.register_checker(db, account.username, account.password)
        return MessageResponse(message=f"성공적으로 체커를 등록했습니다: {account.username}")
    except AlreadyCreatedError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Instagram2FAError:
        logger.warning(f"{account.username}에 2FA가 필요합니다")
        return MessageResponse(message="2FA 코드가 필요합니다.", two_factor_required=True)
    except InstagramLoginError as e:
        raise HTTPException(status_code=401, detail=f"인스타그램 로그인 실패: {e}")
    except Exception as e:
        logger.error(f"체커 {account.username} 등록 실패: {e}")
        raise HTTPException(status_code=500, detail="예상치 못한 오류가 발생했습니다.")

@router.post("/login/2fa", response_model=MessageResponse)
def register_checker_2fa(
    request: InstagramVerificationCodeRequest = Body(...),
    db: Session = Depends(get_db)
):
    try:
        checkers_service.complete_2fa_and_register_checker(
            db, request.username, request.verification_code
        )
        return MessageResponse(
            message=f"2FA를 성공적으로 완료하고 체커를 등록했습니다: {request.username}"
        )
    except (InstagramLoginError, AlreadyCreatedError) as e:
        logger.error(f"체커 {request.username}의 2FA 완료 실패: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"체커 2FA 중 예상치 못한 오류 발생 {request.username}: {e}")
        raise HTTPException(status_code=500, detail="예상치 못한 오류가 발생했습니다.")

