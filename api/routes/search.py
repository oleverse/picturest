from fastapi import status
from api.database.db import get_db
from api.database.models import User, Picture
#from api.repository.comment_service import get_comments_by_picture_id
from api.repository.search import search_by_description, search_by_tag, \
    search_pictures_by_user
from api.schemas.essential import PictureResponse, PictureResponseWithComments
from api.repository import pictures as repository_pictures
from typing import List, Optional, Type
from sqlalchemy.orm import Session
from fastapi import APIRouter, Query, Depends, HTTPException

# Імпортуємо функцію для отримання поточного користувача із системи авторизації
from api.services.auth import auth_service

# Створюємо новий роутер з префіксом та тегом
router = APIRouter(prefix='/search', tags=["Search"])


# Ендпоінт для отримання світлини за її ідентифікатором


@router.get("/description/", response_model=List[PictureResponse])
def search_pictures_by_description(
        search_query: str = Query(..., min_length=1, max_length=100),
        order_by: Optional[str] = Query(None, regex="^(rating|date_added)$"), db: Session = Depends(get_db),
        current_user: str = Depends(auth_service.get_current_user)) -> List[PictureResponse]:
    if order_by == "rating":
        results = search_by_description(db, search_query).order_by(Picture.avg_rating.desc()).all()
    elif order_by == "date_added":
        results = search_by_description(db, search_query).order_by(Picture.created_at.desc()).all()
    else:
        results = search_by_description(db, search_query).all()
    return results


@router.get("/tag/", response_model=List[PictureResponse])
async def search_pictures_by_tag(
        search_query: str = Query(None, min_length=1, max_length=100),
        order_by: Optional[str] = Query(None, regex="^(rating|date_added)$"),
        db: Session = Depends(get_db),
        current_user: str = Depends(auth_service.get_current_user)
) -> list[Type[Picture]]:
    if order_by == "rating":
        results = await search_by_tag(db, search_query, rating=1)
    elif order_by == "date_added":
        results = await search_by_tag(db, search_query, date_added="2023-07-31")
    else:
        results = await search_by_tag(db, search_query)

    return results


# Ендпоінт для пошуку користувачів за іменем, електронною поштою або іншими критеріями GET /pictures/users/search
@router.get("/admin/{picture_id}", response_model=List[PictureResponse])
async def search_user_by_admin_and_moder(user_query: str = Query(None, min_length=1, max_length=100),
                                             db: Session = Depends(get_db),
                                             current_user: User = Depends(auth_service.get_current_user)):
    # Перевіряємо чи користувач є модератором або адміністратором
    if current_user.role_id not in ['admin', 'moderator']:
        raise HTTPException(status_code=403, detail="You don't have permission to perform this action.")

    pictures = search_pictures_by_user(db, user_query)
    return pictures


@router.get("/by_tag/{tag_name}", response_model=List[PictureResponse])
async def get_pictures_by_tag(tag_name: str, db: Session = Depends(get_db)):
    pictures = await repository_pictures.get_picture_by_tag(tag_name, db)
    if not pictures:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Picture with tag {tag_name} not found")
    return pictures
