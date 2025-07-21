from typing import List
from sqlalchemy.orm import Session
from core.database import group_db
from core.entities import InstagramGroup
from core.service.models import GroupDetail

def get_group(db: Session, group_id: int) -> GroupDetail | None:
    group: InstagramGroup = group_db.get(db, group_id)
    if not group:
        return None
    return GroupDetail.from_orm(group)

def get_groups(db: Session) -> List[GroupDetail]:
    groups: List[InstagramGroup] = group_db.load(db)
    return [GroupDetail.from_orm(group) for group in groups]

def save_group(db: Session, type: str) -> GroupDetail:
    new_group = group_db.save(db, type)
    return GroupDetail.from_orm(new_group)


def delete_group(db: Session, id: int) -> None:
    group_db.delete(db, id)
