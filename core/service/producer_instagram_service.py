import logging
import json
from instagrapi import Client
from instagrapi.exceptions import TwoFactorRequired, BadPassword, ChallengeRequired, LoginRequired
from sqlalchemy.orm import Session

from core.exceptions import Instagram2FAError, InstagramLoginError

logger = logging.getLogger(__name__)

# 2FA 처리를 위해 클라이언트 인스턴스를 임시로 저장합니다.
# 실제 운영 환경에서는 Redis 등 캐시를 사용하는 것이 좋습니다.
active_clients = {}

def _get_client_and_login(username: str, password: str = None, verification_code: str = None) -> Client:
    """
    Instagrapi 클라이언트를 초기화하고 로그인 또는 2FA 로그인을 시도합니다.
    """
    cl = active_clients.get(username)
    if not cl:
        cl = Client()
        active_clients[username] = cl
    try:
        if verification_code:
            logger.info(f"{username} 2FA 코드로 로그인 시도 중...")
            cl.login(username=username, password=password, verification_code=verification_code)
        elif password:
            logger.info(f"{username} 비밀번호로 로그인 시도 중...")
            cl.login(username, password)
        else:
            raise ValueError("비밀번호 또는 2FA 코드가 제공되어야 합니다.")
        
        if username in active_clients:
            del active_clients[username]
        return cl

    except TwoFactorRequired as e:
        logger.warning(f"{username}에 2FA가 필요합니다.")
        raise Instagram2FAError("2FA 코드가 필요합니다.") from e
    except BadPassword as e:
        logger.error(f"{username} 로그인 실패: 잘못된 비밀번호", exc_info=True)
        raise InstagramLoginError("로그인에 실패했습니다. 사용자 이름과 비밀번호를 확인하세요.") from e
    except ChallengeRequired as e:
        logger.error(f"{username} 로그인 실패: 챌린지 필요", exc_info=True)
        raise InstagramLoginError("인스타그램 보안 챌린지가 필요합니다. 웹에서 로그인하여 해결하세요.") from e
    except LoginRequired as e:
        logger.error(f"{username} 로그인 실패: 로그인 필요", exc_info=True)
        raise InstagramLoginError("로그인 세션이 만료되었거나 유효하지 않습니다. 다시 로그인해 주세요.") from e
    except Exception as e:
        logger.error(f"{username} 로그인 중 예상치 못한 오류 발생: {e}", exc_info=True)
        raise InstagramLoginError(f"로그인 중 예상치 못한 오류가 발생했습니다: {e}") from e

def login_producer(username: str, password: str) -> str:
    """
    Instagrapi를 사용하여 생산자 로그인을 처리하고 세션 문자열을 반환합니다.
    """
    cl = _get_client_and_login(username, password=password)
    session_string = json.dumps(cl.get_settings())
    logger.info(f"{username} Instagrapi 로그인 성공 및 세션 저장.")
    return session_string

def complete_2fa_producer(username: str, verification_code: str) -> str:
    """
    Instagrapi를 사용하여 생산자 2FA 로그인을 완료하고 세션 문자열을 반환합니다.
    """
    cl = _get_client_and_login(username, verification_code=verification_code)
    session_string = json.dumps(cl.get_settings())
    logger.info(f"{username} Instagrapi 2FA 로그인 성공 및 세션 저장.")
    
    # 2FA 완료 후 임시 클라이언트 제거
    if username in active_clients:
        del active_clients[username]
        
    return session_string

def login_with_session_producer(username: str, session_string: str) -> Client:
    """
    Instagrapi 세션 문자열을 사용하여 로그인합니다.
    """
    cl = Client()
    try:
        cl.set_settings(json.loads(session_string))
        cl.get_timeline_feed() # 세션 유효성 검사
        logger.info(f"{username} Instagrapi 세션으로 로그인 성공.")
        return cl
    except Exception as e:
        logger.error(f"{username} Instagrapi 세션으로 로그인 실패: {e}", exc_info=True)
        raise InstagramLoginError("세션으로 로그인하지 못했습니다. 세션이 만료되었거나 유효하지 않을 수 있습니다.") from e


def like(cl: Client, media_id: str):
    """
    게시물에 좋아요를 누릅니다.
    """
    try:
        cl.media_like(media_id)
        logger.info(f"게시물 {media_id}에 좋아요를 눌렀습니다.")
    except Exception as e:
        logger.error(f"게시물 {media_id}에 좋아요를 누르는 중 오류 발생: {e}", exc_info=True)
        raise

def comment(cl: Client, media_id: str, text: str):
    """
    게시물에 댓글을 작성합니다.
    """
    try:
        cl.media_comment(media_id, text)
        logger.info(f"게시물 {media_id}에 댓글을 작성했습니다: {text}")
    except Exception as e:
        logger.error(f"게시물 {media_id}에 댓글을 작성하는 중 오류 발생: {e}", exc_info=True)
        raise

def media_id(cl: Client, shortcode: str) -> str:
    """
    shortcode를 media_id로 변환합니다.
    """
    try:
        media_pk = cl.media_pk_from_code(shortcode)
        logger.info(f"shortcode {shortcode}를 media_id {media_pk}로 변환했습니다.")
        return str(media_pk)
    except Exception as e:
        logger.error(f"shortcode {shortcode}를 media_id로 변환하는 중 오류 발생: {e}", exc_info=True)
        raise

