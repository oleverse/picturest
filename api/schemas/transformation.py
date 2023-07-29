from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field


class TransformPictureResponse(BaseModel):
    id: int
    picture_url: str
    picture_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ScalePicture(float):
    percent: float = Field(ge=0, le=1)


class TransformCropModel(BaseModel):
    width: int = Field(ge=0, default=400)
    height: int = Field(ge=0, default=400)
    crop: str = 'fill'
    gravity: str = 'auto'
    background: str = 'lightblue'
# gravity="faces", height=800, width=800, crop="thumb"


class RotatePictureModel(BaseModel):
    degree: int = Field(ge=-360, le=360, default=0)


class RadiusImageModel(BaseModel):
    all: int = Field(ge=0, default=0)
    left_top: int = Field(ge=0, default=0)
    right_top: int = Field(ge=0, default=0)
    right_bottom: int = Field(ge=0, default=0)
    left_bottom: int = Field(ge=0, default=0)
    max: bool = Field(default=False)


class SimpleEffectType(str, Enum):
    grayscale = 'grayscale'
    negate = 'negative'
    cartoonify = 'cartoonify'
    oil_paint = 'oil_paint'
    blackwhite = 'black_white'


class SimpleEffectTransformModel(BaseModel):
    effect: SimpleEffectType
    strength: int = Field(ge=0, le=100)


class TransformPictureModel(BaseModel):
    resize: Optional[TransformCropModel]
    rotate: Optional[RotatePictureModel]
    radius: Optional[RadiusImageModel]
    simple_effect: Optional[List[SimpleEffectTransformModel]]


class URLTransformPictureResponse(BaseModel):
    url: str = ''
    id: int



class SaveTransformPictureModel(BaseModel):
    url: str
