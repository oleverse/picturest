from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, validator


class TagModel(BaseModel):
    name: str = Field(max_length=100)


class TagResponse(TagModel):
    id: int

    # user_id: Optional[int]

    class Config:
        orm_mode = True


class PictureBase(BaseModel):
    picture_url: str
    description: Optional[str]
    tags: Optional[List[TagModel]]


class PictureCreate(BaseModel):
    description: Optional[str]
    tags: Optional[list[str]]

    @validator("tags")
    def validate_tags(cls, val):
        if len(val) > 5:
            raise ValueError("Too many tags. Only 5 tags allowed.")
        return val


class PictureResponse(PictureBase):
    id: int
    created_at: datetime
    tags: Optional[List[TagResponse]]

    class Config:
        orm_mode = True

# Додав схеми для коментарів
class CommentBase(BaseModel):
    text: str


class CommentCreate(CommentBase):
    pass


class CommentResponse(CommentBase):
    id: int
    created_at: datetime
    edited: Optional[bool] = False
    edited_at: Optional[datetime]

    class Config:
        orm_mode = True
