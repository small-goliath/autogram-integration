import logging
from typing import List
from sqlalchemy.orm import Session
from core.database import verification_db
from core.entities import UserActionVerification
from core.service.models import VerificationDetail

logger = logging.getLogger(__name__)


def get_verifications_service(db: Session) -> List[VerificationDetail]:
    logger.info("SNS 키우기 인증 목록 조회 요청")
    try:
        verifications = verification_db.get_all_verifications(db)
        logger.info(f"{len(verifications)}개의 인증을 반환합니다.")
        return [VerificationDetail.from_orm(v) for v in verifications]
    except Exception as e:
        logger.error(f"SNS 키우기 인증 목록을 가져오는데 실패했습니다: {e}", exc_info=True)
        raise


def save_verification(session: Session, verification: UserActionVerification) -> bool:
    """검증 결과를 데이터베이스에 저장합니다. 중복은 저장하지 않습니다."""
    return verification_db.save_verification_if_not_exists(session, verification)


def delete_verification(db: Session, verification_id: int) -> bool:
    """인증 정보를 삭제합니다."""
    logger.info(f"{verification_id}번 인증 삭제 요청")
    try:
        result = verification_db.delete_verification_by_id(db, verification_id)
        if result:
            logger.info(f"{verification_id}번 인증을 삭제했습니다.")
        else:
            logger.warning(f"{verification_id}번 인증을 찾지 못해 삭제하지 못했습니다.")
        return result
    except Exception as e:
        logger.error(f"SNS 키우기 인증을 삭제하는데 실패했습니다: {e}", exc_info=True)
        raise
