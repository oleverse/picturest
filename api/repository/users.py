from datetime import datetime
from typing import Type

from libgravatar import Gravatar
from slugify import slugify
from sqlalchemy.orm import Session

from api.database.models import User, BlacklistToken
from api.schemas.essential import UserModel


async def get_users_count(db: Session):
    return len(db.query(User).limit(1).all())


async def get_user_by_email(email: str, db: Session):
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session):
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(
        username=body.username,
        email=body.email,
        password=body.password,
        avatar=avatar
    )
    # new_user = User(**body.model_dump(), avatar=avatar)
    new_user.slug = slugify(body.username)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session):
    user.refresh_token = token
    db.commit()


async def confirm_email(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> Type[User] | None:
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user


async def ban_user(email: str, db: Session) -> None:

    user = await get_user_by_email(email, db)
    user.is_active = False
    db.commit()


async def add_to_blacklist(token: str, db: Session) -> None:
    
    blacklist_token = BlacklistToken(token=token, blacklisted_on=datetime.now())
    db.add(blacklist_token)
    db.commit()
    db.refresh(blacklist_token)
    
    
async def find_blacklisted_token(token: str, db: Session) -> None:

    blacklist_token = db.query(BlacklistToken).filter(BlacklistToken.token == token).first()
    return blacklist_token
    
    
async def remove_from_blacklist(token: str, db: Session) -> None:
   
    blacklist_token = db.query(BlacklistToken).filter(BlacklistToken.token == token).first()
    db.delete(blacklist_token)
