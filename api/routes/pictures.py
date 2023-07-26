from typing import List
from faker import Faker
from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException, Form, Request
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from api.conf.config import settings
from api.repository.comment_service import get_comments_by_picture_id
from api.schemas import PictureBase, PictureResponse, PictureCreate

from api.services.cloud_picture import CloudImage

from api.database.db import get_db
from api.database.models import User, Tag
from api.repository import pictures as repository_pictures

router = APIRouter(prefix='/pictures', tags=["pictures"])


@router.post("/", response_model=PictureResponse, status_code=status.HTTP_201_CREATED)
async def create_picture(request: Request, description: str = Form(None), tags: List = Form(None),
                         file: UploadFile = File(None), db: Session = Depends(get_db)):
    # user
    public_id = Faker().first_name().lower()
    r = CloudImage.upload(file.file, public_id)
    picture_url = CloudImage.get_url_for_picture(public_id, r)

    return await repository_pictures.create_picture(request, description, tags, picture_url, db)


@router.get("/{picture_id}", response_model=PictureResponse)
async def get_picture(picture_id: int, with_comments: bool = True, db: Session = Depends(get_db)):
    picture = await repository_pictures.get_picture(picture_id, db)
    if picture is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    if with_comments:
        picture_with_comments = picture.dict()
        comments = get_comments_by_picture_id(db, picture_id)
        picture_with_comments["comments"] = comments
        return picture_with_comments

    return picture


@router.put("/{picture_id}", response_model=PictureResponse)
async def update_photo(body: PictureCreate, picture_id: int, db: Session = Depends(get_db)):
    picture = await repository_pictures.update_picture(picture_id, body, db)
    if picture is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found")
    return picture


@router.delete("/{picture_id}", response_model=PictureResponse)
async def remove_picture(picture_id: int, db: Session = Depends(get_db)):
    picture = await repository_pictures.remove_picture(picture_id, db)
    if picture is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found")
    return picture


@router.get("/by_tag/{tag_name}", response_model=List[PictureResponse])
async def get_pictures_by_tag(tag_name: str, db: Session = Depends(get_db)):
    # current_user: User = Depends(auth_service.get_current_user)
    pictures = await repository_pictures.get_picture_by_tag(tag_name, db)
    if not pictures:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Picture with tag {tag_name} not found")
    return pictures
