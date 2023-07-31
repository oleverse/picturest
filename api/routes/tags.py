from typing import List

from fastapi import APIRouter, Depends, status, HTTPException, Form, Body, Query
from sqlalchemy.orm import Session

from api.database.db import get_db
from api.repository import tags as repository_tags
from api.routes.pictures import router as pict_router
from api.schemas import TagModel, PictureResponse, TagResponse


tags_router = APIRouter(prefix='/tags', tags=["tags"])


@pict_router.post("/pictures/{picture_id}/tags", response_model=PictureResponse)
async def add_tags(picture_id: int, tags: List[str] = Form(None), db: Session = Depends(get_db)):
    return await repository_tags.add_tags_to_picture(picture_id, tags, db)



@tags_router.get("/tags/", response_model=List[TagModel])
async def get_all_tags(offset: int = Query(0, ge=0), limit: int = Query(100, ge=1), db: Session = Depends(get_db)):
    tags = await repository_tags.get_all_tags(db, skip=offset, limit=limit)
    return tags



@tags_router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = await repository_tags.get_tag(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@tags_router.post("/pictures/{picture_id}/tags", response_model=PictureResponse)
async def add_tags(picture_id: int, tags: List[str] = Form(None), db: Session = Depends(get_db)):
    return await repository_tags.add_tags_to_picture(picture_id, tags, db)


@tags_router.delete("/pictures/{picture_id}/tags/{tag_id}", response_model=TagResponse)
async def delete_tag_from_picture(picture_id: int, tag_id: int, db: Session = Depends(get_db)):
    return await repository_tags.delete_tag_from_picture(picture_id, tag_id, db)




@tags_router.put("/tags/{tag_id}", response_model=TagResponse)
async def edit_tag(
    tag_id: int,
    tag_update: TagModel = Body(...),
    db: Session = Depends(get_db)
    #,current_user: User = Depends(get_current_active_user)
):
    return await repository_tags.edit_tag(tag_id, tag_update, db)

