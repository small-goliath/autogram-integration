import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.routes.payloads import VerificationDetailResponse
from core.db_transaction import get_db
from core.service import verification_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("", response_model=List[VerificationDetailResponse])
def get_verifications(db: Session = Depends(get_db)):
    try:
        return verification_service.get_verifications_service(db)
    except Exception as e:
        logger.error(f"SNS 품앗이 인증 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="인증 목록을 가져오는데 실패했습니다.")
