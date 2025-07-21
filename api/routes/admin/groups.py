from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from api.routes.payloads import CreateInstagramGroupRequest, LoadInstagramGroupResponse, MessageResponse
from core.db_transaction import get_db
from core.service import groups_service

router = APIRouter()

@router.post("", response_model=LoadInstagramGroupResponse)
def create_group(
    request: CreateInstagramGroupRequest = Body(...),
    db: Session = Depends(get_db)
):
    # 그룹 유형은 고유해야 한다고 가정합니다. 서비스/DB 계층에서 이를 처리해야 합니다.
    # 지금은 그대로 진행합니다. 여기서 IntegrityError에 대한 try/except를 사용하는 것이 좋습니다.
    created_group = groups_service.save_group(db, request.type)
    return LoadInstagramGroupResponse.from_orm(created_group)

@router.delete("/{group_id}", response_model=MessageResponse)
def delete_group(group_id: int, db: Session = Depends(get_db)):
    group = groups_service.get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail=f"ID가 {group_id}인 그룹을 찾을 수 없습니다.")
    
    groups_service.delete_group(db, group_id)
    return MessageResponse(message=f"ID가 {group_id}인 그룹이 삭제되었습니다.")
