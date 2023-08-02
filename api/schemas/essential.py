from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict, constr
from api.conf.config import settings


class TagModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str = Field(max_length=100)


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
    picture_id: int


class CommentResponse(CommentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    edited: Optional[bool] = False
    edited_at: Optional[datetime] = None


class PictureResponse(PictureBase):
    id: int
    shared: Optional[bool] = None
    created_at: datetime
    tags: Optional[List[TagModel]] = []


class PictureResponseWithComments(PictureResponse):
    comments: Optional[List[CommentResponse]] = []


class UserModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    email: EmailStr
    password: str = Field(min_length=0, max_length=14)


class UserUpdate(UserModel):
    is_active: bool
    role: str


class UserDb(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    username: str
    email: Optional[EmailStr] = None
    created_at: datetime
    avatar: Optional[str] = None


class UserDbStatus(UserDb):
    is_active: bool


class UserDbExtra(UserDb):
    photos_count: Optional[int] = None
    comments_count: Optional[int] = None


class UserProfileModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    created_at: datetime
    avatar: Optional[str] = None
    number_pictures: Optional[int]
    number_comments: Optional[int]


class UserResponse(BaseModel):
    user: UserDb
    detail: str = 'User successfully created'


class UserProfileUpdate(BaseModel):
    password: constr(min_length=5, max_length=100) = None
    username: str
    email: EmailStr


class UserStatusChange(BaseModel):
    email: EmailStr


class UserStatusResponse(BaseModel):
    username: str
    email: EmailStr
    is_active: bool
    updated_at: datetime


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
