from typing import List, Type

from sqlalchemy.orm import Session

from api.conf.config import settings
from api.database.models import Picture, Tag
from api.repository.tags import create_tag
from api.schemas import PictureCreate
from api.services.cloud_picture import CloudImage


async def create_picture(description: str, tags: List[str], file_path: str, db: Session):
    # If the number of tags is greater than the maximum, return an error message
    if len(tags) > settings.max_tags:
        return f"Error: Too many tags. The maximum is {settings.max_tags}."

    tags_list = []
    if tags:
        tags_list = await transformation_list_to_tag(tags[0].split(","), db)

    picture = Picture(picture_url=file_path, description=description, tags=tags_list)
    db.add(picture)
    db.commit()
    db.refresh(picture)
    # , user_id = user.id
    return picture


def get_tag_by_name(tag_name: str, db: Session) -> Tag | None:
    tag = db.query(Tag).filter(Tag.name == tag_name).first()
    return tag


async def transformation_list_to_tag(tags: list, db: Session) -> List[Tag]:
    # , user
    list_tags = []
    if tags:
        for tag_name in tags:
            tag = await create_tag(tag_name, db)
            # user,
            list_tags.append(tag)
    return list_tags


async def get_picture(picture_id: int, db: Session) -> Picture | None:
    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    return picture


async def get_user_pictures(user_id: int, db: Session) -> list[Type[Picture]]:
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


async def get_picture_by_tag(tag_name: str, db: Session) -> list[Type[Picture]]:
    return db.query(Picture).join(Picture.tags).filter(Tag.name == tag_name).all()
