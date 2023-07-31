from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from api.database.db import get_db
from api.repository import tags as repository_tags
from api.schemas.essential import TagModel

tags_router = APIRouter(prefix='/tags', tags=["tags"])


@tags_router.get("/", response_model=List[TagModel])
async def get_all_tags(db: Session = Depends(get_db)):
    """
    The get_all_tags function returns a list of all tags in the database.

    :param db: Session: Pass the database connection to the function
    :return: A list of tag objects
    """
    tags = await repository_tags.get_all_tags(db)
    return tags


@tags_router.get("/{tag_id}", response_model=TagModel)
async def get_tag(tag_id: int, db: Session = Depends(get_db)):
    """
    The get_tag function returns a single tag from the database.

    :param tag_id: int: Get the tag_id from the url
    :param db: Session: Pass the database session to the function
    :return: The tag with the specified id
    """
    tag = await repository_tags.get_tag(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag
