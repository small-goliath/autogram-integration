import logging
import base64
import logging
import pickle
from instaloader import BadCredentialsException, ConnectionException, TwoFactorAuthRequiredException, instaloader


from core.exceptions import Instagram2FAError, InstagramError, LoginError

logger = logging.getLogger(__name__)

class InstagramLoader:
    def __init__(self, username: str, password: str, verification_code: str = None):
        self.L = instaloader.Instaloader()
        self.username = username
        self.password = password
        self.verification_code = verification_code

    def login(self):
        logger.info(f"[{self.username}] 인스타그램 로그인 시도")
        try:
            self.L.login(self.username, self.password)
        except TwoFactorAuthRequiredException:
            if not self.verification_code:
                raise Instagram2FAError(f"2단계 인증이 필요합니다.")
            try:
                self.L.two_factor_login(self.verification_code)
            except BadCredentialsException as e:
                raise LoginError("잘못된 2FA 코드입니다.")  from e
            except ConnectionException as e:
                raise InstagramError(f"2FA 중 연결 오류: {e}") from e
        except BadCredentialsException as e:
            raise LoginError("잘못된 사용자 이름 또는 비밀번호입니다.") from e
        except ConnectionException as e:
            raise InstagramError(f"로그인 중 연결 오류: {e}") from e
        
    def get_session(self) -> str:
        return self.context_to_string(self.L.context)
    
    @staticmethod
    def context_to_string(context: instaloader.InstaloaderContext) -> str:
        return base64.b64encode(pickle.dumps(context)).decode('utf-8')