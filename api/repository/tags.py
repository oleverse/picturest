from typing import Type

from sqlalchemy.orm import Session

from api.database.models import Tag


async def create_tag(tag_name: str, db: Session):
    """
    The create_tag function creates a new tag in the database.

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


async def get_all_tags(db: Session) -> list[Type[Tag]]:
    """
    The get_all_tags function returns a list of all tags in the database.

    :param db: Session: Pass the database session to the function
    :return: A list of tag objects
    """
    return db.query(Tag).all()


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
