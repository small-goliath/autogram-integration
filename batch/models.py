from pydantic import BaseModel


class KakaoTalk(BaseModel):
    username: str
    link: str