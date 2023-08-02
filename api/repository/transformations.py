from typing import List, Type
from sqlalchemy.orm import Session
from sqlalchemy import and_, exc
from api.database.models import Picture, TransformedPicture, User


async def get_picture_for_transformation(pict_id: int, user: User, db: Session) -> str | None:
    # TODO roles

    picture = db.query(Picture).filter(and_(Picture.id == pict_id, Picture.user_id == user.id)).first()
    picture_path = None
    if picture:
        picture_path = picture.picture_url
    return picture_path


async def set_transform_picture(picture_id: int, modify_url: str, user: User, db: Session) -> TransformedPicture | None:
    """
    The set_transform_picture function queries the Picture in DB with the given picture_id and user.
    If it finds one, it will create a new TransformedPicture object with url and id.
    It will add this to the database and commit it. If there is an integrity error when we try to commit this change
    to our database (i.e., if there already exists such an entry), we rollback these changes so as not

    :param picture_id: int: Specify the picture to be modified
    :param modify_url: str: Store the url of the transformed picture
    :param user: User: Check if the user is allowed to delete the picture
    :param db: Session: Access the database
    :return: A transformed picture object

    """

    # TODO roles

    picture = db.query(Picture).filter(and_(Picture.id == picture_id, Picture.user_id == user.id)).first()
    if picture:
        image = TransformedPicture(url=modify_url, picture_id=picture.id)
        db.add(image)
        try:
            db.commit()
        except exc.IntegrityError:
            db.rollback()
            image = db.query(TransformedPicture) \
                .filter(and_(TransformedPicture.picture_id == picture_id,
                             TransformedPicture.url == modify_url)).first()
        else:
            db.refresh(image)
        return image


async def get_transform_picture(picture_id: int, current_user: User, db: Session) -> TransformedPicture | None:
    #
    # TODO roles - If the user is an admin, then it will return all transformations the picture with the id
    """
    The get_transform_picture function is used to retrieve a single picture from the database.
        The function takes in a picture_id, current_user and db as parameters.
        If the user is an admin, then it will return any transformations of any pictures.
        Otherwise, it will  return only transformations if picture was created by the current user.

    :param picture_id: int: Get the picture id from the database
    :param current_user: User: Check if the user is an admin or not
    :param db: Session: Access the database
    :return: A picture from the database
    """

    pict = db.query(TransformedPicture).join(Picture).filter(
        and_(TransformedPicture.id == picture_id, Picture.user_id == current_user.id)).first()

    return pict


async def remove_transformation(transformation_id: int, current_user: User, db: Session) -> TransformedPicture | None:
    pict = db.query(TransformedPicture).join(Picture).filter(
        and_(TransformedPicture.id == transformation_id, Picture.user_id == current_user.id)).first()
    if pict:
        db.delete(pict)
        db.commit()
    return pict


async def get_all_tr_pict(base_id: int, skip: int, limit: int, user: User, db: Session) -> List[Type[TransformedPicture]]:
    """
    The get_all_tr_pict function returns a list of all transform pictures for the given picture id.

    :param base_id: int: Get the picture id of the picture that was transformed
    :param skip: int: Skip the first n number of items in a list
    :param limit: int: Limit the number of images returned
    :param user: User: current user
    :param db: Session: Access the database
    :return: A list of all the transformations for the picture
    """

    t_pictures = db.query(TransformedPicture)\
        .filter(TransformedPicture.picture_id == base_id).offset(skip).limit(limit).all()

    return t_pictures

