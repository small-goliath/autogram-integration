from typing import List, Optional
from pydantic import BaseModel


class CheckerDetail(BaseModel):
    id: int
    username: str
    session: str
    
    class Config:
        from_attributes = True

class UserDetail(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class GroupDetail(BaseModel):
    id: int
    type: str

    class Config:
        from_attributes = True

class ProducerDetail(BaseModel):
    id: int
    username: str
    enabled: bool
    group_id: int
    session: str

    class Config:
        from_attributes = True

class ConsumerDetail(BaseModel):
    id: int
    username: str
    enabled: bool
    group_id: int

    class Config:
        from_attributes = True

class UnfollowerDetail(BaseModel):
    username: str
    profile_pic_url: str

    class Config:
        from_attributes = True

class UnfollowerCheckStatus(BaseModel):
    status: str
    message: Optional[str] = None
    unfollowers: Optional[List[UnfollowerDetail]] = None
    last_updated: Optional[float] = None

    class Config:
        from_attributes = True

class VerificationDetail(BaseModel):
    id: int
    username: str
    link: str

    class Config:
        from_attributes = True

class SnsRaiseUserCount(BaseModel):
    count: int

    class Config:
        from_attributes = True

class Message(BaseModel):
    message: str

    class Config:
        from_attributes = True

class KakaoTalk(BaseModel):
    username: str
    link: str

    class Config:
        from_attributes = True