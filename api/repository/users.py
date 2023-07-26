from typing import Type

from libgravatar import Gravatar
from slugify import slugify
from sqlalchemy.orm import Session

from api.database.models import User
from api.schemas import UserModel


async def get_user_by_email(email: str, db: Session):

    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session):

    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.dict(), avatar=avatar)
    new_user.slug = slugify(body.username)
    # if len(db.query(User).all()) == 0: uve
    #     new_user.role_id = RoleNames.admin
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session):

    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:

    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> Type[User] | None:
    
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
