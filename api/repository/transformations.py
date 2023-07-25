import cloudinary
import io

from sqlalchemy.orm import Session

from api.database.models import Picture, User, TransformedPicture
from api.services.cloud_picture import CloudImage
from api.schemas_transformation import TransformPictureModel


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



    # if picture:
    #     transformation = []
    #
    #     if body.rotate.use_filter and body.rotate.width and body.rotate.degree:
    #         trans_list = [{'width': f"{body.rotate.width}", 'crop': "scale"}, {'angle': "vflip"},
    #                       {'angle': f"{body.rotate.degree}"}]
    #         [transformation.append(elem) for elem in trans_list]
    #
    #     if transformation:
    #         url = CloudImage.get_transformed_url(picture.picture_url,transformation)
    #         picture.transform_url = url
    #         db.commit()
    #
    #     return picture







