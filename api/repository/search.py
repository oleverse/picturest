from datetime import datetime, timedelta
from typing import Type, Any

from sqlalchemy import or_, and_, Row
from sqlalchemy.orm import Session

from api.database.models import Picture, User, Tag


async def search_pictures_by_query(db: Session, search_query: str = None,
                                   rating: int = None, date_added: str = None) -> list[Type[Picture]]:
    # Починаємо з базового запиту, що вибирає всі світлини
    query = db.query(Picture)

    # Пошук за ключовим словом
    if search_query:
        query = query.filter(or_(Picture.description.ilike(f"%{search_query}%")))

    # Фільтрація за рейтингом
    if rating is not None:
        query = query.filter(Picture.rating >= rating)

    # Фільтрація за датою додавання
    if date_added:
        try:
            date_added = datetime.strptime(date_added, "%Y-%m-%d")
            query = query.filter(and_(Picture.created_at >= date_added,
                                      Picture.created_at < date_added + timedelta(days=1)))
        except ValueError:
            pass

    # Виконуємо запит та повертаємо результат
    return query.all()


# def search_by_tag(db, search_query):
#     return db.query(Picture).filter(Picture.tags.any(text(search_query)))


async def search_by_tag(db: Session, tag_name: str,
                        rating: int = None, date_added: str = None) -> list[Type[Picture]]:
    # Починаємо з базового запиту, що вибирає всі світлини з вказаним тегом
    query = db.query(Picture).join(Picture.tags).filter(Tag.name == tag_name)

    # Фільтрація за рейтингом
    if rating is not None:
        query = query.filter(Picture.rating >= rating)

    # Фільтрація за датою додавання
    if date_added:
        try:
            date_added = datetime.strptime(date_added, "%Y-%m-%d")
            query = query.filter(and_(Picture.created_at >= date_added,
                                      Picture.created_at < date_added + timedelta(days=1)))
        except ValueError:
            pass

    # Виконуємо запит та повертаємо результат
    return query.all()


async def search_users(db: Session, search_query: str = None,
                       date_added: str = None) -> list[Type[User]]:
    # Починаємо з базового запиту, що вибирає всіх користувачів
    query = db.query(User)

    # Пошук за іменем або електронною поштою
    if search_query:
        query = query.filter(or_(User.username.ilike(f"%{search_query}%"),
                                 User.email.ilike(f"%{search_query}%")))

    # Фільтрація за датою додавання - за атрибутом `created_at`
    if date_added:
        try:
            date_added = datetime.strptime(date_added, "%Y-%m-%d")
            query = query.filter(and_(User.created_at >= date_added,
                                      User.created_at < date_added + timedelta(days=1)))
        except ValueError:
            pass

    # Виконуємо запит та повертаємо результат
    return query.all()


def search_by_description(db, search_query):
    return db.query(Picture).filter(Picture.description.ilike(f"%{search_query}%"))


def search_pictures_by_user(db: Session, user_query: str):
    # Ваша логіка пошуку зображень за вказаними користувачами
    # result = db.query(Picture).join(User).filter(User.username.ilike(f"%{user_query}%")).all()
    # pictures = db.query(Picture)
    return db.query(Picture).join(User).filter(User.username.ilike(f"%{user_query}%")).all()
