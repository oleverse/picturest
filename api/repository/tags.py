from typing import List

from sqlalchemy.orm import Session

from api.database.models import Tag


async def get_tag_by_name(tag_name: str, db: Session) -> Tag | None:
    tag = db.query(Tag).filter(Tag.name == tag_name).first()
    return tag


async def get_list_tags(tags: str, user, db: Session) -> List[Tag]:
    list_tags = []
    if len(tags) > 0:
        for tag_name in tags:
            tag = await get_tag_by_name(tag_name, db)
            if not tag:
                tag = create_tag(tag_name, user, db)
            list_tags.append(tag)
    return list_tags


async def create_tag(tag_name, user, db):
    pass



