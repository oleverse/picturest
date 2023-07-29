from typing import List
from fastapi import HTTPException, status, APIRouter, Depends
from sqlalchemy.orm import Session

from api.database.db import get_db
from api.database.models import User

from api.services.auth import auth_service

from api.services.cloud_picture import CloudImage
from api.services.transformation_picture import create_list_transformation

from api.schemas.transformation import TransformPictureModel, URLTransformPictureResponse, TransformPictureResponse

import api.repository.transformations as repo_transform

router = APIRouter(prefix='/picture/transform', tags=['transformation picture'])


@router.post('/{base_picture_id}', response_model=URLTransformPictureResponse, status_code=status.HTTP_200_OK,
             description="simple_effect = 'grayscale','negative','cartoonify','oil_paint' or 'black_white'")
async def transformation_for_picture(base_image_id: int, body: TransformPictureModel,
                                     current_user: User = Depends(auth_service.get_current_user),
                                     db: Session = Depends(get_db)):
    """
    The transformation_for_picture function is used to create transformation of picture.
    It takes in the base_image_id, body and current user as parameters.
    Otherwise, a list of transformations are created using create list transformation function which takes in body as
    parameter.
    Then url is set to transformed url using CloudImage class's get transformed url method which takes in image url
    and transformation list as parameters

    :param base_image_id: int: Get the picture from the database
    :param body: TransformPictureModel: Get the parameters from the request body
    :param current_user: User: Get the current user
    :param db: Session: Access the database
    :return: The url of the transformed picture
    """

    image_url = await repo_transform.get_picture_for_transformation(base_image_id, current_user, db)

    if image_url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found")
    transform_list = create_list_transformation(body)
    url = CloudImage.get_transformed_url(image_url, transform_list)
    img = await repo_transform.set_transform_picture(base_image_id, url, current_user, db)

    return {'id': img.id, 'url': url}


@router.get('/qrcode/{transform_picture_id}', status_code=status.HTTP_200_OK)
async def get_qrcode_for_transform_image(transform_picture_id: int,
                                         current_user: User = Depends(auth_service.get_current_user),
                                         db: Session = Depends(get_db)):
    """
    The get_qrcode_for_transform_image function is used to generate a QR code for the transformed picture.
    The function takes the id of the transform picture (type: integer) and returns a string containing
    the base64 encoded QR code.

    :param transform_picture_id: int: Find the url for picture which was transformed from the DB
    :param current_user: User: Check authentication data of the current user
    :param db: Session: Access the database
    :return: A base64 encoded qr code
    """
    picture = await repo_transform.get_transform_picture(transform_picture_id, current_user, db)
    if picture is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found")
    qr_code = CloudImage.get_qrcode(picture.url)
    return qr_code


@router.delete('/{transformation_id}', status_code=status.HTTP_204_NO_CONTENT)
async def remove_transformed_picture(transformation_id: int,
                                     current_user: User = Depends(auth_service.get_current_user),
                                     db: Session = Depends(get_db)):
    """
    The remove_transformed_picture function is used to remove a transformed image from the database.

    :param transformation_id: int: Identify the transformation that is to be removed
    :param current_user: User: Get the user that is currently logged in
    :param db: Session
    :return: An image object
    """
    el = await repo_transform.remove_transformation(transformation_id, current_user, db)
    if el is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")


# @router.get('/all/{base_picture_id}', response_model=List[TransformPictureResponse], status_code=status.HTTP_200_OK)
# async def get_list_of_transformed_for_picture(base_picture_id: int, skip: int = 0, limit: int = 10,
#                                               current_user: User = Depends(auth_service.get_current_user),
#                                               db: Session = Depends(get_db)):
#     """
#     The get_list_of_transformed_for_picture function returns a list of transformed pictures for the given base image.
#
#     :param base_picture_id: int: Get the base picture id from the database
#     :param skip: int: Skip the first n images in the list
#     :param limit: int: Limit the number of results returned
#     :param current_user: User: Get the current user from the database
#     :param db: Session
#     :return: A list of transformed pictures for a given base image
#     """
#     return await repo_transform.get_all_tr_pict(base_picture_id, skip, limit, current_user, db)
