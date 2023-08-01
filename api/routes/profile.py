from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from api.database.db import get_db
from api.database.models import User, Picture
from api.schemas.essential import UserUpdate, UserDb, UserModel
from api.services.auth import auth_service

router = APIRouter(prefix="/profile", tags=['profile'])


def get_user_by_username(db: Session, username: str) -> UserModel | None:
    return db.query(User).filter(User.username == username).first()


def update_user(db: Session, user_update: UserUpdate, current_user: User) -> UserModel:
    user = get_user_by_username(db, current_user.username)

    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    for field, value in user_update.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user


def get_uploaded_photos_count(username: str, db: Session = Depends(get_db)) -> int:
    try:
        # Get the user from the database using the username
        user = db.query(User).filter(User.username == username).first()

        if not user:
            return 0

        # Count the number of uploaded photos for the user
        photos_count = db.query(func.count(Picture.id)).filter(Picture.id == user.id).scalar()

        return photos_count
    finally:
        db.close()


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
                      current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    user = username

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    photos_count = get_uploaded_photos_count(username=user.username, db=db)

    user_data = UserDb(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
        avatar=user.avatar,
        photos_count=photos_count)
    return user_data


@router.put("/profile/me", response_model=UserModel)
def edit_own_profile(user_update: UserUpdate, db: Session = Depends(get_db),
                     current_user: User = Depends(auth_service.get_current_user)):
    user = update_user(db, user_update, current_user)
    return user
