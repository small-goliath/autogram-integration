import logging
import base64
import pickle
import instaloader
from sqlalchemy.orm import Session
from core.Instagram import InstagramLoader
from core.exceptions import Instagram2FAError, InstagramLoginError
from core.service import instagram_session_service

logger = logging.getLogger(__name__)

# 이것은 여전히 상태를 유지하지만 여기에 캡슐화되어 있습니다.
# 더 나은 해결책은 데이터베이스나 캐시(예: Redis)를 사용하여 보류 중인 2FA 세션을 저장하는 것입니다.
active_loaders = {}

def login(db: Session, username: str, password: str) -> None:
    """
    인스타그램에 로그인하고 성공하면 세션을 저장합니다.
    2FA가 필요한 경우 Instagram2FAError를 발생시킵니다.
    다른 로그인 실패 시 InstagramLoginError를 발생시킵니다.
    """
    logger.info(f"{username} 로그인을 시도합니다.")
    try:
        instagram_loader = InstagramLoader(username=username, password=password)
        instagram_loader.login()
        
        instagram_session_service.save_session(db, username, instagram_loader.L.context)
        logger.info(f"{username} 로그인에 성공하고 세션을 저장했습니다.")

    except Instagram2FAError:
        logger.warning(f"{username}에 2FA가 필요합니다.")
        # 2FA 시도를 위해 컨텍스트에 비밀번호 저장
        instagram_loader.L.context.password = password
        active_loaders[username] = instagram_loader
        raise

    except Exception as e:
        logger.error(f"{username} 로그인 실패: {e}", exc_info=True)
        error_message = "로그인에 실패했습니다. 사용자 이름과 비밀번호를 확인하세요."
        if "checkpoint" in str(e).lower():
            error_message = "체크포인트가 필요합니다. 브라우저를 통해 로그인하여 해결하세요."
        raise InstagramLoginError(error_message) from e

def login_2fa(db: Session, username: str, verification_code: str) -> None:
    """
    2FA 로그인 시도를 완료합니다.
    실패 시 InstagramLoginError를 발생시킵니다.
    """
    logger.info(f"{username}의 2FA 로그인을 시도합니다.")
    instagram_loader: InstagramLoader = active_loaders.get(username)

    if not instagram_loader:
        raise InstagramLoginError("로그인 세션이 만료되었거나 유효하지 않습니다. 다시 로그인해 주세요.")

    try:
        instagram_loader.verification_code = verification_code
        instagram_loader.login()
        
        instagram_session_service.save_session(db, username, instagram_loader.L.context)
        logger.info(f"{username}의 2FA를 성공적으로 완료하고 세션을 저장했습니다.")
        
        del active_loaders[username]

    except Exception as e:
        logger.error(f"{username}의 2FA 완료 실패: {e}", exc_info=True)
        if username in active_loaders:
            del active_loaders[username]
        raise InstagramLoginError("잘못된 2FA 코드입니다.") from e

def login_with_session(username: str, session: str) -> instaloader.Instaloader:
    """
    인스타그램에 세션을 사용하여 로그인합니다.
    성공하면 Instaloader 인스턴스를 반환합니다.
    """
    logger.info(f"{username} 세션으로 로그인을 시도합니다.")
    try:
        L = instaloader.Instaloader()
        unpickled_context = pickle.loads(base64.b64decode(session))
        L.context = unpickled_context
        logger.info(f"{username} 세션으로 로그인 성공.")
        return L
    except Exception as e:
        logger.error(f"{username} 세션으로 로그인 실패: {e}", exc_info=True)
        raise InstagramLoginError("세션으로 로그인하지 못했습니다. 세션이 만료되었거나 유효하지 않을 수 있습니다.") from e
