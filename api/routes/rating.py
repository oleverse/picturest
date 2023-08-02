from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Path
from sqlalchemy.orm import Session

from api.database.db import get_db
from api.schemas.essential import RatingModel
from api.repository import rating
from api.services.auth import auth_service
# from api.services.roles import RoleChecker
from api.database.models import User  # , RoleNames


router = APIRouter(prefix='/rating', tags=["rating"])


# allowed_get_all_ratings = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder])
# allowed_create_ratings = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
# allowed_edit_ratings = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
# allowed_remove_ratings = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder])
# allowed_user_picture_rate = RoleChecker([UserRoleEnum.admin])
# allowed_commented_by_user = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])


@router.post("/pictures/{picture_id}/{rate}", response_model=RatingModel)
# , dependencies=[Depends(allowed_create_ratings)])
async def create_rate(picture_id: int, rate: int = Path(description='Rate in the range of one to five', ge=1, le=5),
                      db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    
    new_rate = await rating.create_rate(picture_id, rate, db, current_user)
    if new_rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There is no picture with this ID')
    return new_rate


@router.put("/edit/{rate_id}/{new_rate}", response_model=RatingModel)  # , dependencies=[Depends(allowed_edit_ratings)])
async def edit_rate(rate_id: int, new_rate: int, db: Session = Depends(get_db),
                    current_user: User = Depends(auth_service.get_current_user)):
    
    edited_rate = await rating.edit_rate(rate_id, new_rate, db, current_user)
    if edited_rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Rating not found or unavailable')
    return edited_rate


@router.delete("/delete/{rate_id}", response_model=RatingModel)  # , dependencies=[Depends(allowed_remove_ratings)])
async def delete_rate(rate_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    
    deleted_rate = await rating.delete_rate(rate_id, db, current_user)
    if deleted_rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Rating not found or unavailable')
    return deleted_rate


@router.get("/all", response_model=List[RatingModel])  # , dependencies=[Depends(allowed_get_all_ratings)])
async def all_rates(db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    
    comments = await rating.get_all_ratings(db, current_user)
    if comments is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Rating not found')
    return comments


@router.get("/all_my", response_model=List[RatingModel])  # , dependencies=[Depends(allowed_commented_by_user)])
async def my_rates(db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):

    comments = await rating.get_my_rating(db, current_user)
    if comments is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Rating not found')
    return comments


@router.get("/user_picture/{user_id}/{picture_id}", response_model=RatingModel)
# , dependencies=[Depends(allowed_user_picture_rate)])
async def user_rate_picture(user_id: int, picture_id: int, db: Session = Depends(get_db),
                            current_user: User = Depends(auth_service.get_current_user)):
    
    rate = await rating.get_user_rate_picture(user_id, picture_id, db, current_user)
    if rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    return rate
