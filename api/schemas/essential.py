from datetime import datetime, date
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


class PictureCreate(BaseModel):
    description: Optional[str]
    tags: Optional[list[str]] = []

    @field_validator("tags")
    def validate_tags(cls, val):
        if len(val) > settings.max_tags:
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
    # model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    comments: Optional[List[CommentResponse]] = []


class UserModel(BaseModel):

    username: str
    email: EmailStr
    password: str = Field(min_length=0, max_length=14)


class UserDb(BaseModel):

    id: int
    username: str
    email: EmailStr
    created_at: datetime
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):

    user: UserDb
    detail: str = 'User successfully created'


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class RequestEmail(BaseModel):
    email: EmailStr
