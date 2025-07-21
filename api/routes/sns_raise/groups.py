from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.routes.payloads import LoadInstagramGroupResponse
from core.db_transaction import get_db
from core.service import groups_service
from core.service.models import GroupDetail

router = APIRouter()

@router.get("", response_model=List[LoadInstagramGroupResponse])
def get_all_groups(db: Session = Depends(get_db)):
    groups: List[GroupDetail] = groups_service.get_groups(db)
    return [LoadInstagramGroupResponse.from_orm(group) for group in groups]
