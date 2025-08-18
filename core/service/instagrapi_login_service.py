import logging
import re
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from instagrapi import Client
from core.Instagram import InstagramClient
from core.exceptions import Instagram2FAError, InstagramLoginError, LoginError
from core.service import instagram_session_service

load_dotenv()

logger = logging.getLogger(__name__)

# 2FA 처리를 위한 임시 클라이언트 저장소
active_clients = {}

def login(db: Session, username: str, password: str) -> Client:
    try:
        instagram_client = InstagramClient(username=username, password=password)
        instagram_client.login()
        
        settings = instagram_client.cl.get_settings()
        instagram_session_service.save_session(db, username, settings)
        logger.info(f"{username} 로그인에 성공하고 세션을 저장했습니다.")

        return instagram_client.cl

    except Instagram2FAError:
        logger.warning(f"{username}에 2FA가 필요합니다.")
        # 2FA 시도를 위해 클라이언트와 비밀번호 저장
        active_clients[username] = {'username': username, 'password': password}
        raise

    except Exception as e:
        logger.error(f"{username} 로그인 실패: {e}")
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

def login_2fa(db: Session, username: str, verification_code: str) -> Client:
    logger.info(f"{username}의 2FA 로그인을 시도합니다.")
    client_info = active_clients.get(username)

    if not client_info:
        raise InstagramLoginError("로그인 세션이 만료되었거나 유효하지 않습니다. 다시 로그인해 주세요.")

    try:
        password = client_info['password']
        instagram_client = InstagramClient(username=username, password=password, verification_code=verification_code)
        instagram_client.login()
        
        settings = instagram_client.cl.get_settings()
        instagram_session_service.save_session(db, username, settings)
        logger.info(f"{username}의 2FA를 성공적으로 완료하고 세션을 저장했습니다.")
        
        del active_clients[username]

        return instagram_client.cl

    except LoginError as e:
        logger.error(f"{username}의 2FA 완료 실패: {e}")
        if username in active_clients:
            del active_clients[username]
        raise InstagramLoginError("잘못된 2FA 코드입니다.") from e
    except Exception as e:
        logger.error(f"{username}의 로그인 실패: {e}")
        if username in active_clients:
            del active_clients[username]
        raise LoginError("로그인할 수 없습니다.") from e

def login_with_session(username: str, session: str) -> Client:
    logger.info(f"{username} 세션으로 로그인을 시도합니다.")
    try:
        instagram_client = InstagramClient(username=username, session=session)
        instagram_client.login_with_session()

        logger.info(f"{username} 세션으로 로그인 성공.")
        return instagram_client.cl
    except Exception as e:
        logger.error(f"{username} 세션으로 로그인 실패: {e}")
        raise InstagramLoginError("세션으로 로그인하지 못했습니다. 세션이 만료되었거나 유효하지 않을 수 있습니다.") from e