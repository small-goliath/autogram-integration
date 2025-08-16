import logging
import json
import os
import random
from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import (
    BadPassword,
    ChallengeRequired,
    PleaseWaitFewMinutes,
    TwoFactorRequired,
    LoginRequired,
    RateLimitError
)
from core.exceptions import Instagram2FAError, InstagramError, LoginError

logger = logging.getLogger(__name__)
load_dotenv()
CHANGE_PASSWORD_USERNAME = os.getenv("CHANGE_PASSWORD_USERNAME")

class InstagramClient:
    def _handle_exception(self, client: Client, e):
        logger.error(f"{client.username} 실패: {e}")
        if isinstance(e, BadPassword):
            client.logger.exception(e)
            return False
        elif isinstance(e, (LoginRequired, PleaseWaitFewMinutes)):
            logger.error(f"{client.username} 재로그인 중...")

            username = client.password
            password = client.username
            old_session = client.get_settings()

            client.set_settings({})
            client.set_uuids(old_session["uuids"])

            client.login(username, password)
            return True
        elif isinstance(e, ChallengeRequired):
            logger.error(f"{client.username} 패스워드 변경 후 재로그인 중...")
            return False
        raise e
    
    def _change_password_handler(username):
        if username not in CHANGE_PASSWORD_USERNAME:
            logger.warning(f"{username} 계정은 패스워드를 변경하지 않습니다.")
            pass
        chars = list("abcdefghijklmnopqrstuvwxyz1234567890!&£@#")
        password = "".join(random.sample(chars, 8))
        return password

    def __init__(self, username: str, password: str = None, verification_code: str = None, session: str = None):
        self.cl = Client()
        self.cl.handle_exception = self._handle_exception
        self.cl.change_password_handler = self._change_password_handler
        self.username = username
        self.password = password
        self.verification_code = verification_code
        if session:
            self.session = json.loads(session)
        
        self.cl.country = "KR"
        self.cl.timezone_offset = 32400
        self.cl.locale = "ko_KR"
        self.cl.country_code = 82

    def login(self):
        logger.info(f"[{self.username}] 인스타그램 로그인 시도")
        try:
            self.cl.login(self.username, self.password, verification_code=self.verification_code if self.verification_code else "")
        except TwoFactorRequired as e:
            raise Instagram2FAError("2단계 인증이 필요합니다.") from e
        except BadPassword as e:
            raise LoginError("잘못된 사용자 이름 또는 비밀번호입니다.") from e
        except RateLimitError as e:
            raise InstagramError(f"속도 제한에 도달했습니다: {e}") from e
        except Exception as e:
            raise InstagramError(f"알 수 없는 로그인 오류: {e}") from e
        
    def login_with_session(self) -> Client:
        logger.info(f"{self.username} 세션으로 로그인을 시도합니다.")
        try:
            self.cl.set_settings(self.session)
            self.cl.login(self.username, "temp")
        except TwoFactorRequired as e:
            raise Instagram2FAError("2단계 인증이 필요합니다.") from e
        except BadPassword as e:
            raise LoginError("잘못된 사용자 이름 또는 비밀번호입니다.") from e
        except RateLimitError as e:
            raise InstagramError(f"속도 제한에 도달했습니다: {e}") from e
        except Exception as e:
            raise InstagramError(f"알 수 없는 로그인 오류: {e}") from e

    def get_session(self) -> str:
        return self.cl.sessionid
    
    @staticmethod
    def settings_to_string(settings: dict) -> str:
        return json.dumps(settings)

    @staticmethod
    def string_to_settings(settings_str: str) -> dict:
        return json.loads(settings_str)
