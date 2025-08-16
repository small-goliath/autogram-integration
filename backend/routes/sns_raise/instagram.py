import logging
from fastapi import APIRouter, HTTPException, Body, Depends
from sqlalchemy.orm import Session

from backend.routes.payloads import InstagramLoginRequest, InstagramVerificationCodeRequest, MessageResponse
from core.db_transaction import get_db
from core.exceptions import Instagram2FAError, InstagramLoginError
from core.service import instagrapi_login_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/login", response_model=MessageResponse)
async def login(
    request: InstagramLoginRequest = Body(...),
    db: Session = Depends(get_db)
):
    logger.info(f"사용자 {request.username} 로그인 시도")
    try:
        instagrapi_login_service.login(db, request.username, request.password)
        return MessageResponse(message=f"성공적으로 로그인했습니다: {request.username}")
    except Instagram2FAError:
        logger.warning(f"{request.username}에 2FA가 필요합니다")
        return MessageResponse(message="2FA 코드가 필요합니다.", two_factor_required=True)
    except InstagramLoginError as e:
        logger.error(f"{request.username} 로그인 실패: {e}", exc_info=True)
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"{request.username} 로그인 중 예상치 못한 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="예상치 못한 서버 오류가 발생했습니다.")

@router.post("/login/2fa", response_model=MessageResponse)
async def login_2fa(
    request: InstagramVerificationCodeRequest = Body(...),
    db: Session = Depends(get_db)
):
    logger.info(f"사용자 {request.username}의 2FA 로그인 시도")
    try:
        instagrapi_login_service.login_2fa(db, request.username, request.verification_code)
        return MessageResponse(message=f"2FA로 성공적으로 로그인했습니다: {request.username}")
    except InstagramLoginError as e:
        logger.error(f"{request.username}의 2FA 로그인 실패: {e}", exc_info=True)
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"{request.username}의 2FA 로그인 중 예상치 못한 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="예상치 못한 서버 오류가 발생했습니다.")

@router.post("/logout")
async def logout():
    # 이 기능은 올바르게 구현되어야 합니다.
    # 데이터베이스에서 세션을 삭제하는 작업이 포함될 것입니다.
    # 예: instagram_session_service.delete_session(db, username)
    logger.info("로그아웃 시도")
    raise HTTPException(status_code=501, detail="로그아웃 기능이 구현되지 않았습니다.")
