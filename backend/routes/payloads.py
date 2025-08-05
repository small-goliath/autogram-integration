from typing import List, Optional
from pydantic import BaseModel

from core.service.models import ConsumerDetail, ProducerDetail, UserDetail

class InstagramLoginRequest(BaseModel):
    username: str
    password: str

class InstagramVerificationCodeRequest(BaseModel):
    username: str
    verification_code: str

class CreateInstagramGroupRequest(BaseModel):
    type: str

class DeleteInstagramGroupRequest(BaseModel):
    id: int

class LoadInstagramGroupResponse(BaseModel):
    id: int
    type: str

    class Config:
        from_attributes = True

class SnsRaiseUserResponse(BaseModel):
    count: int
    details: List[UserDetail]

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class CreateCheckerRequest(BaseModel):
    username: str
    password: str
    verification_code: str | None = None

class RegisterCheckerRequest(BaseModel):
    username: str
    password: str

class CheckerDetailResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class ProducerLoginRequest(BaseModel):
    username: str
    password: str
    group_id: int

class ProducerVerificationCodeRequest(BaseModel):
    username: str
    verification_code: str
    group_id: int

class ProducersResponse(BaseModel):
    count: int
    details: List[ProducerDetail]

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class CreateConsumerRequest(BaseModel):
    username: str
    group_id: int

class ConsumersResponse(BaseModel):
    count: int
    details: List[ConsumerDetail]

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class MessageResponse(BaseModel):
    message: str
    two_factor_required: Optional[bool] = False

    class Config:
        from_attributes = True

class UnfollowerDetailResponse(BaseModel):
    username: str
    profile_pic_url: str

    class Config:
        from_attributes = True

class UnfollowerCheckStatusResponse(BaseModel):
    status: str
    message: Optional[str] = None
    unfollowers: Optional[List[UnfollowerDetailResponse]] = None
    last_updated: Optional[float] = None

    class Config:
        from_attributes = True

class VerificationDetailResponse(BaseModel):
    username: str
    link: str

    class Config:
        from_attributes = True
