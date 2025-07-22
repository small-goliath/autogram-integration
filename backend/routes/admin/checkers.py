import logging
from typing import List
from fastapi import APIRouter, HTTPException, Response, Depends, Body
from sqlalchemy.orm import Session

from backend.routes.payloads import CheckerDetailResponse, RegisterCheckerRequest
from core.db_transaction import get_db
from core.exceptions import AlreadyCreatedError, NotFoundError
from core.service import checkers_service

router = APIRouter()
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

@router.post("", response_model=CheckerDetailResponse, status_code=201)
def register_checker(
    account: RegisterCheckerRequest = Body(...),
    db: Session = Depends(get_db)
):
    try:
        new_checker = checkers_service.register_checker(db, account.username)
        return new_checker
    except AlreadyCreatedError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"체커 {account.username} 등록 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="예상치 못한 오류가 발생했습니다.")