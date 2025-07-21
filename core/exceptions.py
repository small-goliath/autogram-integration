class ServiceError(Exception):
    """서비스 계층 오류에 대한 기본 예외입니다."""
    pass

class InstagramLoginError(ServiceError):
    """인스타그램 로그인 과정에서 발생하는 오류입니다."""
    pass

class SearchCommentError(Exception):
    pass

class CommentError(Exception):
    pass

class LikeError(Exception):
    pass

class LoginError(Exception):
    pass

class InstagramError(Exception):
    pass

class Instagram2FAError(Exception):
    pass

class AlreadyCreatedError(Exception):
    pass

class InvalidPropertyError(Exception):
    pass


class UserNotPermittedError(Exception):
    """사용자가 작업을 수행할 수 있는 권한이 없을 때 발생합니다."""
    pass

class NotFoundError(ServiceError):
    """요청한 리소스를 찾을 수 없을 때 발생합니다."""
    pass