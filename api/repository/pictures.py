from typing import List
from fastapi import Request
from sqlalchemy.orm import Session

from api.database.models import Picture, User, Tag
from api.schemas import PictureCreate, PictureBase
from api.services.cloud_picture import CloudImage


async def create_picture(request: Request, description: str, tags: List, file_path: str, db: Session):
    tags_list = []
    if tags:
        tags_list = transformation_list_to_tag(tags[0].split(","), db)
    picture = Picture(picture_url=file_path, description=description, tags=tags_list)
    db.add(picture)
    db.commit()
    db.refresh(picture)
    # , user_id = user.id
    return picture


def get_tag_by_name(tag_name: str, db: Session) -> Tag | None:
    tag = db.query(Tag).filter(Tag.name == tag_name).first()
    return tag


def transformation_list_to_tag(tags: list, db: Session) -> List[Tag]:
    # , user
    list_tags = []
    if tags:
        for tag_name in tags:
            tag = get_tag_by_name(tag_name, db)
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.commit()
                db.refresh(tag)
                # user,
            list_tags.append(tag)
    return list_tags


async def get_picture(picture_id: int, db: Session) -> Picture | None:
    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    return picture


async def get_user_pictures(user_id: int, db: Session) -> List[Picture]:

    pictures = db.query(Picture).filter(Picture.user_id == user_id).all()
    return pictures


async def remove_picture(picture_id: int, db: Session):

    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    if picture:
        public_id = picture.picture_url.split("/")[-1]
        CloudImage.destroy(public_id)
        db.delete(picture)
        db.commit()
    return picture


async def update_picture(picture_id: int, body: PictureCreate, db: Session):
    # , user: User
    picture = db.query(Picture).filter(Picture.id == picture_id).first()

    if picture:
        tags_list = transformation_list_to_tag(body.tags, db)
        # user,
        picture.description = body.description
        picture.tags = tags_list
        db.commit()
        db.refresh(picture)
    return picture


async def get_picture_by_tag(tag_name: str, db: Session) -> List[Picture]:
    return db.query(Picture).join(Picture.tags).filter(Tag.name == tag_name).all()
