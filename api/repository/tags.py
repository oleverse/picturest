from typing import Type

from sqlalchemy.orm import Session

from api.database.models import Tag


async def create_tag(tag_name: str, db: Session):
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
    return db.query(Tag).all()


async def get_tag(tag_id: int, db: Session) -> Type[Tag] | None:
    return db.query(Tag).filter(Tag.id == tag_id).first()
