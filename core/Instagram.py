import logging
import json
from instagrapi import Client
from instagrapi.exceptions import (
    BadPassword,
    TwoFactorRequired,
    LoginRequired,
    ChallengeRequired,
    RateLimitError
)
from core.exceptions import Instagram2FAError, InstagramError, LoginError

logger = logging.getLogger(__name__)

class InstagramClient:
    def __init__(self, username: str, password: str, verification_code: str = None):
        self.cl = Client()
        self.username = username
        self.password = password
        self.verification_code = verification_code
        
        self.cl.country = "KR"
        self.cl.timezone_offset = 32400
        self.cl.locale = "ko_KR"
        self.cl.country_code = 82
        self.cl.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"

    def login(self):
        logger.info(f"[{self.username}] 인스타그램 로그인 시도")
        try:
            self.cl.login(self.username, self.password, verification_code=self.verification_code if self.verification_code else "")
        except TwoFactorRequired as e:
            raise Instagram2FAError("2단계 인증이 필요합니다.") from e
        except BadPassword as e:
            raise LoginError("잘못된 사용자 이름 또는 비밀번호입니다.") from e
        except LoginRequired as e:
            raise LoginError("로그인이 필요합니다.") from e
        except ChallengeRequired as e:
            raise InstagramError(f"챌린지가 필요합니다: {e}") from e
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
