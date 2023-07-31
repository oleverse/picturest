from typing import List, Type

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from api.database.models import Picture, Tag, User
from api.repository.tags import create_tag
from api.schemas.essential import PictureCreate
from api.services.cloud_picture import CloudImage
from api.conf.config import settings


async def create_picture(description: str, tags: List[str], file_path: str, shared: bool, db: Session, user: User):
    """
    The create_picture function creates a new picture in the database.
        Args:
            description (str): The description of the picture.
            tags (List[str]): A list of tags for the picture.
            file_path (str): The path to where the image is stored.

    :param description: str: Set the description of the picture
    :param tags: List[str]: Create a list of tags
    :param file_path: str: Store the file path of the picture in the database
    :param db: Session: Access the database
    :param user: User: Get the user id from the database
    :return: The picture object
    """
    tags_list = []

    if tags:
        tags_list = await transformation_list_to_tag(tags, user, db)

    picture = Picture(picture_url=file_path, description=description, tags=tags_list, shared=shared, user_id=user.id)
    db.add(picture)
    db.commit()
    db.refresh(picture)

    return picture


def get_tag_by_name(tag_name: str, db: Session) -> Tag | None:
    tag = db.query(Tag).filter(Tag.name == tag_name).first()
    return tag


async def transformation_list_to_tag(tags: list, user: User, db: Session) -> List[Tag]:
    if not user.role.can_post_tag:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to add tags")

    list_tags = []
    if tags:
        for tag_name in tags:
            tag = await create_tag(tag_name.strip(), db)
            list_tags.append(tag)
    return list_tags


async def get_picture(picture_id: int, db: Session) -> Picture | None:
    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    return picture


async def get_user_pictures(user_id: int, db: Session, limit: int = 10, offset: int = 0) -> list[Type[Picture]]:
    pictures = db.query(Picture).filter(Picture.user_id == user_id).limit(limit).offset(offset).all()
    return pictures


async def get_all_pictures(db: Session, limit: int = 10, offset: int = 0) -> list[Type[Picture]]:
    pictures = db.query(Picture).filter(Picture.shared.is_(True)).limit(limit).offset(offset).all()

    return pictures


async def remove_picture(picture_id: int, user: User, db: Session):
    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    if picture:

        if picture.user_id != user.id and not user.role.can_del_not_own_pict:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="This picture belong's to another person. You are not allowed to remove it!")
        if picture.user_id == user.id:
            public_id = picture.picture_url.split("/")[-1]
            CloudImage.destroy(public_id)
            db.delete(picture)
            db.commit()
            return picture


async def update_picture(picture_id: int, body: PictureCreate, user: User, db: Session):
    picture = db.query(Picture).filter(Picture.id == picture_id and Picture.user_id == user.id).first()
    if picture:
        if picture.user_id != user.id and not user.role.can_mod_not_own_pict:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="This picture belong's to another person. You are not allowed to update it!")
        if body.tags is None:
            picture.tags = []
        elif body.tags:
            tag_names = [t.name for t in picture.tags]
            tag_names.extend(body.tags)
            tag_names = list(set(tag_names))
            if len(tag_names) > settings.max_tags:
                raise HTTPException(status_code=400, detail=f"Too many tags. The maximum is {settings.max_tags}. "
                                                            f"The picture already has {len(picture.tags)} tags")
            picture.tags = await transformation_list_to_tag(tag_names, db)
            
        picture.description = body.description
        picture.update = True
        picture.shared = body.shared
        db.commit()
        db.refresh(picture)
        return picture


async def get_picture_by_tag(tag_name: str, db: Session) -> list[Type[Picture]]:
    return db.query(Picture).join(Picture.tags).filter(Tag.name == tag_name).all()
