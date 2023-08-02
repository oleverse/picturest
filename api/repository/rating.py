from typing import Type

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from starlette import status

from api.database.models import Rating, User, Picture, RoleNames


async def create_rate(picture_id: int, rate: int, db: Session, user: User) -> Rating:
   
    self_picture = db.query(Picture).filter(and_(Picture.id == picture_id, Picture.user_id == user.id)).first()
    already_voted = db.query(Rating).filter(and_(Rating.picture_id == picture_id, Rating.user_id == user.id)).first()
    picture_exists = db.query(Picture).filter(Picture.id == picture_id).first()
    if self_picture:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail='You cannot vote on your own picture')
    elif already_voted:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail='Sorry, you have already voted')
    elif picture_exists:
        new_rate = Rating(picture_id=picture_id, rate=rate, user_id=user.id)
        db.add(new_rate)
        db.commit()
        db.refresh(new_rate)
        return new_rate


async def edit_rate(rate_id: int, new_rate: int, db: Session, user: User) -> Type[Rating] | None:
    
    rate = db.query(Rating).filter(Rating.id == rate_id).first()
    if user.role in [RoleNames.admin, RoleNames.moderator] or rate.user_id == user.id:
        if rate:
            rate.rate = new_rate
            db.commit()
    return rate


async def delete_rate(rate_id: int, db: Session, user: User) -> Type[Rating]:
   
    rate = db.query(Rating).filter(Rating.id == rate_id).first()
    if rate:
        db.delete(rate)
        db.commit()
    return rate


async def get_all_ratings(db: Session, user: User) -> list[Type[Rating]]:
    
    all_ratings = db.query(Rating).all()
    return all_ratings


async def get_my_rating(db: Session, user: User) -> list[Type[Rating]]:
   
    my_rating = db.query(Rating).filter(Rating.user_id == user.id).all()
    return my_rating


async def get_user_rate_picture(user_id: int, picture_id: int, db: Session, user: User) -> Type[Rating] | None:
    
    user_rate_picture = db.query(Rating)\
        .filter(and_(Rating.picture_id == picture_id, Rating.user_id == user_id)).first()
    return user_rate_picture
