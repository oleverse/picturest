from typing import List, Type

from sqlalchemy.orm import Session

from api.conf.config import settings
from api.database.models import Picture, Tag, User
from api.repository.tags import create_tag
from api.schemas import PictureCreate
from api.services.cloud_picture import CloudImage


async def create_picture(description: str, tags: List[str], file_path: str, db: Session, user: User):
    tags_list = []
    if tags:
        tags_list = await transformation_list_to_tag(tags, db)
    picture = Picture(picture_url=file_path, description=description, tags=tags_list, user_id=user.id)
    db.add(picture)
    db.commit()
    db.refresh(picture)
    return picture


def get_tag_by_name(tag_name: str, db: Session) -> Tag | None:
    tag = db.query(Tag).filter(Tag.name == tag_name).first()
    return tag


async def transformation_list_to_tag(tags: list, db: Session) -> List[Tag]:

    list_tags = []
    if tags:
        for tag_name in tags:
            tag = await create_tag(tag_name, db)
            list_tags.append(tag)
    return list_tags


async def get_picture(picture_id: int, db: Session) -> Picture | None:
    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    return picture


async def get_user_pictures(user_id: int, db: Session) -> list[Type[Picture]]:
    pictures = db.query(Picture).filter(Picture.user_id == user_id).all()
    return pictures


async def remove_picture(picture_id: int, user: User, db: Session):

    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    if picture:

        # TODO - кому дозволимо видаляти , наприклад - адміністратор може видаляти, що хоче, а юзер - свої
        # if user.role == admin or picture.user_id == user.id
        if picture.user_id == user.id:
            public_id = picture.picture_url.split("/")[-1]
            CloudImage.destroy(public_id)
            db.delete(picture)
            db.commit()
    return picture


async def update_picture(picture_id: int, body: PictureCreate, user: User, db: Session):

    picture = db.query(Picture).filter(Picture.id == picture_id).first()

    if picture:

        # TODO - кому дозволимо видаляти , наприклад - адмністратор може видаляти, що хоче, а юзер - свої
        # if user.role == admin or picture.user_id == user.id
        if picture.user_id == user.id:
            tags_list = transformation_list_to_tag(body.tags, db)
            picture.description = body.description
            picture.tags = tags_list
            db.commit()
            db.refresh(picture)
    return picture


async def get_picture_by_tag(tag_name: str, db: Session) -> list[Type[Picture]]:
    return db.query(Picture).join(Picture.tags).filter(Tag.name == tag_name).all()
