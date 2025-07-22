from typing import List
from fastapi import APIRouter, HTTPException, Body, Depends
from sqlalchemy.orm import Session

from backend.routes.payloads import ConsumersResponse, CreateConsumerRequest, MessageResponse
from core.db_transaction import get_db
from core.exceptions import AlreadyCreatedError, InvalidPropertyError
from core.service import consumer_service
from core.service.models import ConsumerDetail

router = APIRouter()

@router.post("", response_model=MessageResponse)
async def create_consumer(
    consumer: CreateConsumerRequest = Body(...),
    db: Session = Depends(get_db)
):
    try:
        consumer_service.save_consumer(db, consumer.username, consumer.group_id)
    except AlreadyCreatedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except InvalidPropertyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return MessageResponse(message="소비자 계정이 성공적으로 등록되었습니다.")

@router.get("", response_model=ConsumersResponse)
async def search_consumers(db: Session = Depends(get_db)):
    consumers: List[ConsumerDetail] = consumer_service.get_consumers(db)
    return ConsumersResponse(count=len(consumers), details=consumers)
