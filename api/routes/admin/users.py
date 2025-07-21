from typing import List
from fastapi import APIRouter
from api.routes.payloads import SnsRaiseUserResponse
from core.service.models import UserDetail
from core.service.users_service import delete_user, get_users, save_user

router = APIRouter()

@router.get("", response_model=list[SnsRaiseUserResponse])
def get():
    users: List[UserDetail] = get_users()
    return [SnsRaiseUserResponse(id=user.id, username=user.username) for user in users]

@router.post("/{username}")
def save(username: str):
    return save_user(username)

@router.delete("/{username}")
def delete(username: str):
    return delete_user(username)
