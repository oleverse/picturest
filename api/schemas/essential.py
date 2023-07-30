from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from api.conf.config import settings


class TagModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(max_length=100)


class TagResponse(TagModel):
    id: int


class PictureBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    picture_url: str
    description: Optional[str] = None
    tags: Optional[List[TagModel]] = []
    shared: Optional[bool] = True


class PictureCreate(BaseModel):
    description: Optional[str]
    tags: Optional[list[str]] = []
    shared: Optional[bool] = True

    @field_validator("tags")
    def validate_tags(cls, val):
        if val and len(val) > settings.max_tags:
            raise ValueError(f"Too many tags. Only {settings.max_tags} tags allowed.")
        return val


# Додав схеми для коментарів
class CommentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    text: str


class CommentCreate(CommentBase):
    pass


class CommentResponse(CommentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    edited: Optional[bool] = False
    edited_at: Optional[datetime] = None


class PictureResponse(PictureBase):
    id: int
    shared: bool
    created_at: datetime


class PictureResponseWithComments(PictureResponse):
    comments: Optional[List[CommentResponse]] = []


class UserModel(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=0, max_length=14)


class UserDb(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    created_at: datetime
    avatar: Optional[str] = None


class UserResponse(BaseModel):
    user: UserDb
    detail: str = 'User successfully created'


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class RequestEmail(BaseModel):
    email: EmailStr


class RatingBase(BaseModel):
    rate: int


class RatingModel(RatingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    post_id: int
    user_id: int
