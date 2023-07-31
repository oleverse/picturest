from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.database.db import get_db
from api.database.models import User
from api.schemas.essential import UserUpdate, UserDb, UserModel
from api.services.auth import auth_service

router = APIRouter(prefix="/profile", tags=['profile'])


def get_user_by_username(db: Session, username: str) -> UserModel | None:
    return db.query(User).filter(User.username == username).first()


def update_user(db: Session, user_update: UserUpdate, current_user: User) -> UserModel:
    user = get_user_by_username(db, current_user.username)

    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user


@router.get("/{username}", response_model=UserDb)
def view_user_profile(username: str, db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    # Check if the user is allowed to view profiles
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    # Fetch the user from the database
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


@router.get("/profile/me", response_model=UserDb)
def view_user_profile(username: str = Depends(auth_service.get_current_user),
                      current_user: User = Depends(auth_service.get_current_user)):

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    user = username

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_data = UserDb(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
        avatar=user.avatar)
    return user_data


@router.put("/profile/me", response_model=UserModel)
def edit_own_profile(user_update: UserUpdate, db: Session = Depends(get_db),
                     current_user: User = Depends(auth_service.get_current_user)):
    user = update_user(db, user_update, current_user)
    return user
