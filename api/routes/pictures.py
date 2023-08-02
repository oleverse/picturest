from typing import List
from faker import Faker
from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException, Form, Query
from sqlalchemy.orm import Session

from api.database.db import get_db
from api.database.models import User
from api.repository import pictures as repository_pictures
from api.repository.comments import get_comments_by_picture_id

from api.schemas.essential import PictureResponse, PictureCreate, PictureResponseWithComments
from api.services.auth import auth_service
from api.services.cloud_picture import CloudImage
from api.conf.config import settings

router = APIRouter(prefix='/pictures', tags=["pictures"])


@router.post("/", response_model=PictureResponse, status_code=status.HTTP_201_CREATED)
async def create_picture(description: str = Form(None), tags: List = Form(None),
                         file: UploadFile = File(None), shared: bool = True, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The create_picture function creates a new picture in the database.

    :param description: str: Get the Description of the picture from the request
    :param tags: List: Get the tags from the request
    :param file: UploadFile: Receive the file from the client
    :param shared: bool: Indicate if the picture is shared or not
    :param db: Session: Get the database session if user has permission
    :param current_user: User: Get the user that is currently logged in
    :return: A picture object as a json object
    """

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
    """
    The get_picture function returns a picture by its id.
        If the with_comments parameter is set to True, it will also return all comments for that picture.

    :param picture_id: int: Get the picture by id
    :param with_comments: bool: Determine whether the comments should be returned or not
    :param db: Session: Access the database
    :param current_user: User: Get the current user
    :return: A picture object
    """
    picture = await repository_pictures.get_picture(picture_id, db)
    
    if picture is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found")

    if with_comments:
        picture_with_comments = picture.__dict__
        comments = await get_comments_by_picture_id(db, picture_id)
        picture_with_comments["comments"] = comments
        return picture_with_comments

    return picture


@router.get("/pictures/", response_model=List[PictureResponseWithComments])
async def get_all_pictures(limit: int = Query(10, le=100), offset: int = 0, db: Session = Depends(get_db)):
    """
    The get_all_pictures function returns a list of all pictures in the database which is allowed for sharing
        The limit and offset parameters are used to paginate the results.

    :param limit: int: Limit the number of pictures returned
    :param le: Limit the number of pictures returned
    :param offset: int: Skip the first offset number of pictures
    :param db: Session: Pass the database session to the function
    :return: A list of pictures
    """
    pictures = await repository_pictures.get_all_pictures(limit=limit, offset=offset, db=db)
    if pictures is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Picture not found')
    return pictures


@router.get("/user_pictures/", response_model=List[PictureResponse])
async def get_user_pictures(limit: int = Query(10, le=100), offset: int = 0,
                            current_user: User = Depends(auth_service.get_current_user),
                            db: Session = Depends(get_db)):
    """
    The get_user_pictures function returns a list of pictures posted by the current user.

    :param limit: int: Limit the number of pictures returned
    :param le: Limit the number of pictures that can be returned in a single request
    :param offset: int:
    :param current_user: User: Get the current user
    :param db: Session: Get a database session, which is required for creating and updating pictures
    :return: A list of pictures created by the current user
    """
    pictures = await repository_pictures.get_user_pictures(limit=limit, offset=offset, user_id=current_user.id, db=db)
    if pictures is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'For {current_user.username} picture not found')
    return pictures


@router.put("/{picture_id}", response_model=PictureResponse)
async def update_picture(body: PictureCreate, picture_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_picture function updates a picture in the database.
        The function takes three arguments:
            - body: PictureCreate, which is a Pydantic model that contains all of the information needed to update a picture.
            - picture_id: int, the id of the picture to be updated.  This value comes from path parameters and must be passed into this function as such (see below).
            - db: Session = Depends(get_db), which is an SQLAlchemy session object

    :param body: PictureCreate: Get the data from the request body
    :param picture_id: int: Identify the picture to be updated
    :param db: Session: Get the database session
    :param current_user: User: Get the current user
    :return: A picture object

    """
    picture = await repository_pictures.update_picture(picture_id, body, current_user, db)
    if picture is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Picture with id {picture_id} not found")
    return picture


@router.delete("/{picture_id}", response_model=PictureResponse)
async def remove_picture(picture_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The remove_picture function removes a picture from the database.

    :param picture_id: int: Specify the picture to be removed
    :param db: Session: Get the database session
    :param current_user: User: Get the current user from the database
    :return: A picture object
    """
    picture = await repository_pictures.remove_picture(picture_id, current_user, db)
    if picture is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found")
    return picture
