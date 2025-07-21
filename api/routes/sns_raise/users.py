import logging
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.routes.payloads import SnsRaiseUserResponse
from core.db_transaction import get_db
from core.service import users_service
from core.service.models import UserDetail

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("", response_model=SnsRaiseUserResponse)
def get_all_users(db: Session = Depends(get_db)):
    users: List[UserDetail] = users_service.get_users(db)
    return SnsRaiseUserResponse(count=len(users), details=users)
