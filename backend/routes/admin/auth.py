import logging
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.db_transaction import get_db
from core.service import admin_service

router = APIRouter()
logger = logging.getLogger(__name__)

class AdminLoginPayload(BaseModel):
    username: str
    api_key: str

async def verify_admin(
    x_admin_username: str = Header(...),
    x_admin_key: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    API 요청 헤더를 통해 관리자를 인증하는 의존성
    """
    is_valid = admin_service.verify_admin_credentials(db, x_admin_username, x_admin_key)
    if not is_valid:
        raise HTTPException(status_code=403, detail="인증 자격 증명이 유효하지 않습니다.")
    return {"username": x_admin_username}


@router.post("/login")
def login(payload: AdminLoginPayload, db: Session = Depends(get_db)):
    """
    관리자 로그인을 처리합니다.
    """
    is_valid = admin_service.verify_admin_credentials(db, payload.username, payload.api_key)
    if not is_valid:
        logger.warning(f"관리자 로그인 실패: {payload.username}")
        raise HTTPException(status_code=401, detail="아이디 또는 API 키가 올바르지 않습니다.")
    
    logger.info(f"관리자 로그인 성공: {payload.username}")
    return {"message": "로그인 성공"}
