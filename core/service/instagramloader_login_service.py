import base64
import logging
import json
import os
import pickle
import re
import instaloader
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from core.Instagram import InstagramLoader
from core.exceptions import Instagram2FAError, InstagramLoginError, LoginError
from core.service import instagramloader_session_service

load_dotenv()

logger = logging.getLogger(__name__)

active_loaders = {}

def login(db: Session, username: str, password: str) -> None:
    logger.info(f"{username} 로그인을 시도합니다.")
    try:
        instagram_loader = InstagramLoader(username=username, password=password)
        instagram_loader.login()
        
        instagramloader_session_service.save_session(db, username, instagram_loader.L.context)
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
        error_str = str(e)
        if "checkpoint" in error_str.lower():
            match = re.search(r"(https://www.instagram.com/challenge/[\S]+)", error_str)
            if match:
                url = match.group(1)
                error_message = f"인스타그램 보안 체크포인트가 필요합니다. 아래 URL을 브라우저에 복사하여 본인 인증을 완료한 후 다시 시도해주세요.\n\n{url}"
            else:
                error_message = "체크포인트가 필요합니다. 브라우저를 통해 로그인하여 해결하세요. (인증 URL을 가져올 수 없습니다)"
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
        
        instagramloader_session_service.save_session(db, username, instagram_loader.L.context)
        logger.info(f"{username}의 2FA를 성공적으로 완료하고 세션을 저장했습니다.")
        
        del active_loaders[username]

    except LoginError as e:
        logger.error(f"{username}의 2FA 완료 실패: {e}", exc_info=True)
        if username in active_loaders:
            del active_loaders[username]
        raise InstagramLoginError("잘못된 2FA 코드입니다.") from e
    except Exception as e:
        logger.error(f"{username}의 로그인 실패: {e}", exc_info=True)
        if username in active_loaders:
            del active_loaders[username]
        raise LoginError("로그인할 수 없습니다.") from e

def login_with_session(username: str, session: str) -> instaloader.Instaloader:
    """
    인스타그램에 세션을 사용하여 로그인합니다.
    성공하면 Instaloader 인스턴스를 반환합니다.
    """
    logger.info(f"{username} 세션으로 로그인을 시도합니다.")
    try:
        L = instaloader.Instaloader(download_pictures=False,
                                    download_videos=False,
                                    download_video_thumbnails=False,
                                    download_geotags=False,
                                    save_metadata=False,
                                    compress_json=False)
        unpickled_context = pickle.loads(base64.b64decode(session))
        L.context = unpickled_context
        
        if L.test_login() != username:
            raise InstagramLoginError("세션이 유효하지 않습니다.")
        
        logger.info(f"{username} 세션으로 로그인 성공.")
        return L
    except Exception as e:
        logger.error(f"{username} 세션으로 로그인 실패: {e}", exc_info=True)
        raise InstagramLoginError("세션으로 로그인하지 못했습니다. 세션이 만료되었거나 유효하지 않을 수 있습니다.") from e

def login_with_session_file(username: str) -> instaloader.Instaloader:
    """
    세션 파일을 사용하여 인스타그램에 로그인합니다.
    성공하면 Instaloader 인스턴스를 반환합니다.
    """
    logger.info(f"{username} 세션 파일로 로그인을 시도합니다.")
    try:
        L = instaloader.Instaloader(download_pictures=False,
                                    download_videos=False,
                                    download_video_thumbnails=False,
                                    download_geotags=False,
                                    save_metadata=False,
                                    compress_json=False,
                                    max_connection_attempts=1)
        
        session_dir = os.getenv("INSTALOADER_SESSION_DIR")
        if not session_dir:
            raise EnvironmentError("INSTALOADER_SESSION_DIR 환경 변수가 설정되지 않았습니다.")
            
        session_filename = f"{session_dir}/session-{username}"

        L.load_session_from_file(username, session_filename)
        L.save_session_to_file()

        if L.test_login() != username:
            raise InstagramLoginError("세션이 유효하지 않습니다.")
        
        logger.info(f"{username} 세션 파일로 로그인 성공.")
        return L
    except FileNotFoundError:
        logger.error(f"세션 파일을 찾을 수 없습니다: {session_filename}")
        raise InstagramLoginError(f"세션 파일을 찾을 수 없습니다: {session_filename}")
    except Exception as e:
        logger.error(f"{username} 세션 파일로 로그인 실패: {e}", exc_info=True)
        raise InstagramLoginError("세션 파일로 로그인하지 못했습니다.") from e

