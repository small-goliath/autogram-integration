import logging
import json
import os
import random
import onetimepass as otp
from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import (
    BadPassword,
    PleaseWaitFewMinutes,
    TwoFactorRequired,
    LoginRequired,
    RateLimitError
)
from core.db_transaction import read_only_transactional, transactional
from core.exceptions import Instagram2FAError, InstagramError, LoginError
from core.service import checkers_service
from core.service.models import CheckerDetail

logger = logging.getLogger(__name__)
load_dotenv()
CHANGE_PASSWORD_USERNAME = os.getenv("CHANGE_PASSWORD_USERNAME")
otps_json = os.getenv("INSTAGRAM_OTPS")
otps = json.loads(otps_json) if otps_json else {}

def get_OTP(username: str) -> str:
    otp_num = otp.get_totp(otps[username])
    logger.info(f"{username}의 otp는 {otp_num}입니다.")
    return str(otp_num)

class InstagramClient:
    def _handle_exception(self, client: Client, e):
        logger.info(f"{client.username} 예외 핸들러 실행 : {e}")

        if isinstance(e, BadPassword):
            client.logger.exception(e)
            return False
        elif isinstance(e, (LoginRequired, PleaseWaitFewMinutes)):
            with read_only_transactional() as db:
                checker: CheckerDetail = checkers_service.get_checker_by_username(db, client.username)
                if not checker:
                    logger.info(f"{client.username}는 로그인할 수 없습니다...")
                    return False

            logger.info(f"{client.username}/{client.password} 재로그인 중...")
            username = client.username
            password = checker.pwd
            old_session = client.get_settings()

            client.set_settings({})
            client.set_uuids(old_session["uuids"])

            try:
                client.login(username, password, verification_code=get_OTP(username))
                client.get_notes()
                return True
            except:
                return False
        raise e
    
    def _change_password_handler(username):
        if username not in CHANGE_PASSWORD_USERNAME:
            logger.warning(f"{username} 계정은 패스워드를 변경하지 않습니다.")
            pass
        with transactional() as db:
            chars = list("abcdefghijklmnopqrstuvwxyz1234567890!&£@#")
            password = "".join(random.sample(chars, 8))
            logger.info(f"{username}의 패스워드를 {password}로 변경합니다.")
            checkers_service.update_password(username, password)
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
            with read_only_transactional() as db:
                checker: CheckerDetail = checkers_service.get_checker_by_username(db, self.username)
                if checker:
                    self.cl.login(self.username, checker.pwd)
                else:
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