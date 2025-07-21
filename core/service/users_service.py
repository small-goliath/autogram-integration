from typing import List
from sqlalchemy.orm import Session
from core.database import user_db
from core.entities import SnsRaiseUser
from core.service.models import UserDetail

def get_users(db: Session) -> List[UserDetail]:
    users: List[SnsRaiseUser] = user_db.load(db)
    return [UserDetail.from_orm(user) for user in users]

def save_user(db: Session, username: str) -> UserDetail:
    new_user = user_db.save(db, username)
    return UserDetail.from_orm(new_user)

def delete_user(db: Session, username: str) -> bool:
    return user_db.delete(db, username)
