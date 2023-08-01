from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.database.db import get_db
from api.database.models import User

import api.repository.users as repository_users

from api.schemas.essential import UserModel, UserResponse, UserDb, UserProfileModel, UserUpdate
from api.services.auth import auth_service

router = APIRouter(prefix='/users', tags=["users"])


@router.get("/me/", response_model=UserProfileModel)
async def read_users_me(username: str, current_user: User = Depends(auth_service.get_current_user),
                        db: Session = Depends(get_db)):
    """
    The read_users_me function is a GET endpoint that returns the current user's information.

    :param username: str: Unique username
    :param current_user: User: Pass the user object to the function
    :param db: Session: Get the database session
    :return: The user object
    """
    user = await repository_users.get_user_profile(username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with name {username} not found")
    return user


@router.get('/all', response_model=List[UserDb])
async def get_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    all_users = await repository_users.get_all_users(skip, limit, User(id=1), db)
    if all_users is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")
    return all_users


@router.put("/update_user_self", response_model=UserDb)
async def update_user_self(
        body: UserModel,
        user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)):
    user = await repository_users.update_user_self(body, user, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")
    return user


@router.put("/update_user_as_admin", response_model=UserModel)
async def update_user_as_admin(
        body: UserUpdate,
        user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)):
    user = await repository_users.update_user_as_admin(body, user, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND_OR_DENIED")
    return user