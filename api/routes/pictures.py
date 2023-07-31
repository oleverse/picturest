from typing import List
from faker import Faker
from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException, Form, Query
from sqlalchemy.orm import Session

from api.database.db import get_db
from api.database.models import User
from api.repository import pictures as repository_pictures
from api.repository.comments import get_comments_by_picture_id
from api.repository.searching_service import get_picture_by_id

from api.schemas.essential import PictureResponse, PictureCreate, PictureResponseWithComments
from api.services.auth import auth_service
from api.services.cloud_picture import CloudImage
from api.conf.config import settings

router = APIRouter(prefix='/pictures', tags=["pictures"])


@router.post("/", response_model=PictureResponse, status_code=status.HTTP_201_CREATED)
async def create_picture(description: str = Form(None), tags: List = Form(None),
                         file: UploadFile = File(None), shared: bool = True, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    # let's transform our tags from Form into a list of strings    
    tags = tags[0].strip().split(',') if tags and tags[0] else []

    if len(tags) > settings.max_tags:
        raise HTTPException(status_code=400, detail=f"Too many tags. The maximum is {settings.max_tags}.")

    public_id = Faker().first_name().lower()
    try:
        r = CloudImage.upload(file.file, public_id)
    except (ValueError, AttributeError) as v_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(v_err))
    else:
        picture_url = CloudImage.get_url_for_picture(public_id, r)
        return await repository_pictures.create_picture(description, tags, picture_url, shared, db, current_user)

@router.get("/{picture_id}", response_model=PictureResponseWithComments)
async def get_picture(picture_id: int, with_comments: bool = True, db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    picture = await get_picture_by_id(picture_id, current_user, db)
    if picture is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found")

    if with_comments:
        picture_with_comments = picture.__dict__
        comments = await get_comments_by_picture_id(db, picture_id)
        picture_with_comments["comments"] = comments
        return picture_with_comments

    return picture

@router.get("/pictures/", response_model=List[PictureResponse])
async def get_all_pictures(limit: int = Query(10, le=100), offset: int = 0, db: Session = Depends(get_db)):
    pictures = await repository_pictures.get_all_pictures(limit=limit, offset=offset, db=db)
    if pictures is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Picture not found')
    return pictures


@router.get("/user_pictures/", response_model=List[PictureResponse])
async def get_user_pictures(limit: int = Query(10, le=100), offset: int = 0,
                            current_user: User = Depends(auth_service.get_current_user),
                            db: Session = Depends(get_db)):
    pictures = await repository_pictures.get_user_pictures(limit=limit, offset=offset, user_id=current_user.id, db=db)
    if pictures is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'For {current_user.username} picture not found')
    return pictures


@router.put("/{picture_id}", response_model=PictureResponse)
async def update_picture(body: PictureCreate, picture_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    picture = await repository_pictures.update_picture(picture_id, body, current_user, db)
    if picture is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found")
    return picture


@router.delete("/{picture_id}", response_model=PictureResponse)
async def remove_picture(picture_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    picture = await repository_pictures.remove_picture(picture_id, current_user, db)
    if picture is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found")
    return picture


