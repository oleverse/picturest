from typing import Type, List

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from fastapi import HTTPException

from api.conf.config import settings
from api.database.models import Tag, Picture
from api.schemas.essential import TagModel


async def get_or_create_tag(tag_name: str, db: Session):
    """
    Creates a new tag if it doesn't exist.

    :param tag_name: str: Specify the name of the tag to be created
    :param db: Session: Pass in the database session
    :return: The new tag object, or the existing tag object if it already exists
    """
    existing_tag = db.query(Tag).filter(Tag.name == tag_name).first()
    if existing_tag is None:
        new_tag = Tag(name=tag_name)
        db.add(new_tag)
        db.commit()
        db.refresh(new_tag)
        return new_tag
    else:
        return existing_tag


def process_tags(tags: List[str]) -> List[str]:
    processed_tags = []
    for tag_str in tags:
        split_tags = tag_str.split(',')
        processed_tags.extend([tag.strip() for tag in split_tags])
    if len(processed_tags) > 5:
        raise HTTPException(status_code=400, detail="Too many tags. Only 5 tags allowed.")
    return processed_tags


async def get_all_tags(db: Session, skip: int = 0, limit: int = 100):
    tags = db.query(Tag).offset(skip).limit(limit).all()
    
    return tags


async def get_tag(tag_id: int, db: Session) -> Type[Tag] | None:
    """
    The get_tag function takes in a tag_id and db Session object,
    and returns the Tag object with that id. If no such tag exists,
    it returns None.

    :param tag_id: int: Specify the id of the tag to be returned
    :param db: Session: Access the database
    :return: A tag object
    """
    return db.query(Tag).filter(Tag.id == tag_id).first()


async def add_tags_to_picture(picture_id: int, tags: List[str], db: Session):
    # Start a transaction
    transaction = db.begin()

    picture = db.query(Picture).get(picture_id)

    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")

    processed_tags = process_tags(tags)

    new_tags = []

    for tag_name in processed_tags:
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
            try:
                db.flush()  # Just add to the transaction, don't commit yet
            except IntegrityError:
                db.rollback()
                tag = db.query(Tag).filter(Tag.name == tag_name).first()
            db.refresh(tag)
        new_tags.append(tag)

    if len(picture.tags) + len(new_tags) > settings.max_tags:
        transaction.rollback()
        raise HTTPException(status_code=400, detail=f"Too many tags. Only {settings.max_tags} tags allowed.")

    picture.tags.extend(new_tags)
    try:
        transaction.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Tag already exists.")

    return picture


async def delete_tag_from_picture(picture_id: int, tag_id: int, db: Session):
    picture = db.query(Picture).get(picture_id)

    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")

    tag = db.query(Tag).get(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    if tag in picture.tags:
        picture.tags.remove(tag)
        db.commit()
        db.refresh(picture)

        return picture
    else:
        raise HTTPException(status_code=404, detail="The picture does not have such tag.")


async def edit_tag(tag_id: int, tag_update: TagModel, db: Session):
    tag = db.query(Tag).get(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    tag.name = tag_update.name
    db.commit()
    db.refresh(tag)

    return tag


