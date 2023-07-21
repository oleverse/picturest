from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


class TagModel(BaseModel):
    name: str = Field(max_length=100)


class TagResponse(TagModel):
    id: int
    user_id: Optional[int]

    class Config:
        orm_mode = True


class PictureBase(BaseModel):
    picture_url: str
    description: Optional[str]
    tags: Optional[List[TagModel]]


class PictureCreate(BaseModel):
    description: Optional[str]
    tags: Optional[List[str]]


class PictureResponse(PictureBase):
    id: int
    created_at: datetime
    tags: Optional[List[TagResponse]]

    class Config:
        orm_mode = True
