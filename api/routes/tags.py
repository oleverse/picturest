from typing import List

from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException,Form, Request
from sqlalchemy.orm import Session

from api.conf.config import settings

from api.schemas import TagModel

from api.repository import tags as repository_tags
from api.database.db import get_db
from api.database.models import User, Tag



tags_router = APIRouter(prefix='/tags', tags=["tags"])

@tags_router.get("/", response_model=List[TagModel])
async def get_all_tags(db: Session = Depends(get_db)):
    tags = await repository_tags.get_all_tags(db)
    return tags

@tags_router.get("/{tag_id}", response_model=TagModel)
async def get_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = await repository_tags.get_tag(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag
