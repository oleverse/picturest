from typing import List

from sqlalchemy.orm import Session

from api.database.models import Picture, User
from api.schemas import PictureCreate
from api.repository import tags as repository_tags


async def create_picture(body: PictureCreate, file_path: str, db: Session, user: User):

    tags_list = repository_tags.get_list_tags(body.tags, user, db)

    picture = Picture(picture_url=file_path, description=body.description, user_id=user.id, tags=tags_list)
    db.add(picture)
    db.commit()
    db.refresh(picture)

    return picture


async def get_picture(picture_id: int, db: Session) -> Picture | None:

    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    return picture


async def get_user_pictures(user_id: int, db: Session) -> List[Picture]:

    pictures = db.query(Picture).filter(Picture.user_id == user_id).all()
    return pictures


async def remove_picture(picture_id: int, db: Session):

    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    if picture:
        db.delete(picture)
        db.commit()
    return picture


async def update_picture(picture_id: int, body: PictureCreate, db: Session, user: User):

    picture = db.query(Picture).filter(Picture.id == picture_id).first()

    if picture:
        tags_list = repository_tags.get_list_tags(body.tags, user, db)

        picture.description = body.description
        picture.tags = tags_list
        db.commit()
        db.refresh(picture)
    return picture
