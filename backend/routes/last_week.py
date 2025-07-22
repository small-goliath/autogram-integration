from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.db_transaction import get_db
from core.service import request_by_week_service

router = APIRouter()

@router.get("/requests")
def get_last_week_requests(db: Session = Depends(get_db)):
    return request_by_week_service.get_all_requests(db)
