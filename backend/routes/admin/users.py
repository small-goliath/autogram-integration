from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.routes.admin.auth import verify_admin
from core.db_transaction import get_db

router = APIRouter(dependencies=[Depends(verify_admin)])
from backend.routes.payloads import SnsRaiseUserResponse
from core.service.models import UserDetail
from core.service.users_service import delete_user, get_users, save_user

router = APIRouter()

@router.get("", response_model=SnsRaiseUserResponse)
def get(db: Session = Depends(get_db)):
    users: List[UserDetail] = get_users(db)
    return SnsRaiseUserResponse(count=len(users), details=users)

@router.post("/{username}")
def save(username: str, db: Session = Depends(get_db)):
    return save_user(db, username)

@router.delete("/{username}")
def delete(username: str, db: Session = Depends(get_db)):
    return delete_user(db, username)
