from sqlalchemy.orm import Session

from api.database.models import Picture, TransformedPicture


async def get_picture_for_transformation(pict_id: int, db: Session) -> str | None:
    # user: User,
    # TODO roles

    picture = db.query(Picture).filter(Picture.id == pict_id).first()
    # Picture.user_id == user.id,

    picture_path = None
    if picture:
        picture_path = picture.picture_url

    return picture_path


async def set_transform_picture(picture_id: int, modify_url: str, db: Session) -> TransformedPicture | None:
    # current_user: User,
    # TODO roles

    image = None
    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    if picture:
        image = TransformedPicture(url=modify_url, picture_id=picture.id)
        db.add(image)
        db.commit()
        db.refresh(image)
    return image


async def get_transform_picture(picture_id: int, db: Session) -> TransformedPicture | None:
    # current_user: User,
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

    pict = db.query(TransformedPicture).filter(TransformedPicture.id == picture_id).first()
    print(pict, 'rewt')
    # join(Picture).
    # if current_user.user_role == UserRole...:
    #     img = db.query(TransformedPicture).filter(TransformedPicture.id == picture_id).first()
    # else:
    # Post.user_id == current_user.id)).first()

    return pict







