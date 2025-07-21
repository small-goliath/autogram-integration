import logging
from sqlalchemy.orm import Session

from core.entities import InstagramGroup

logger = logging.getLogger(__name__)

def get(db: Session, group_id: int):
    logger.info(f"인스타그램 그룹 {group_id}을 조회합니다.")
    group = db.query(InstagramGroup).filter(InstagramGroup.id==group_id).first()
    return group

def load(db: Session):
    logger.info("인스타그램 그룹을 조회합니다.")
    groups = db.query(InstagramGroup).all()
    return groups
    
def save(db: Session, type: str) -> InstagramGroup:
    logger.info(f"인스타그램 그룹 {type}을 저장합니다.")
    new_group = InstagramGroup(type=type)
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return new_group

def delete(db: Session, id: int):
    logger.info(f"인스타그램 그룹 {id}을 삭제합니다.")
    db.query(InstagramGroup).filter(InstagramGroup.id==id).delete()
    db.commit()