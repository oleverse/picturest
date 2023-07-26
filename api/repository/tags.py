from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import exc
from api.database.models import Tag, User, RoleNames

async def create_tag(db: Session, tag_name: str):
    existing_tag = db.query(Tag).filter(Tag.name == tag_name).first()
    if existing_tag is None:
        new_tag = Tag(name=tag_name)
        db.add(new_tag)
        db.commit()
        db.refresh(new_tag)
        return new_tag
    else:
        return existing_tag


async def get_all_tags(db: Session) -> List[Tag]:
    return db.query(Tag).all()

async def get_tag(tag_id: int, db: Session) -> Tag:
    return db.query(Tag).filter(Tag.id == tag_id).first()