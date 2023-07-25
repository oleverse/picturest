from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict


class TagModel(BaseModel):
    name: str = Field(max_length=100)


class TagResponse(TagModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    # user_id: Optional[int]


class PictureBase(BaseModel):
    picture_url: str
    description: Optional[str]
    tags: Optional[List[TagModel]]


class PictureCreate(BaseModel):
    description: Optional[str]
    tags: Optional[list[str]]

    @field_validator("tags")
    def validate_tags(cls, val):
        if len(val) > 5:
            raise ValueError("Too many tags. Only 5 tags allowed.")
        return val


class PictureResponse(PictureBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    tags: Optional[List[TagResponse]]

    class Config:
        orm_mode = True
