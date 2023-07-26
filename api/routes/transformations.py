from typing import List
from fastapi import HTTPException, status, APIRouter, Depends
from sqlalchemy.orm import Session

import api.repository.transformations as repo_transform

from api.database.db import get_db
from api.database.models import User
from api.schemas import PictureResponse
from api.schemas_transformation import TransformPictureModel, URLTransformPictureResponse, SaveTransformPictureModel, \
    TransformPictureResponse

# from api.services.auth import auth_service
from api.services.transformatioon_picture import create_list_transformation
from api.services.cloud_picture import CloudImage

router = APIRouter(prefix='/picture/transform', tags=['transformation picture'])


@router.post('/{base_picture_id}', response_model=URLTransformPictureResponse, status_code=status.HTTP_200_OK,
             description="simple_effect = 'grayscale','negative','cartoonify','oil_paint' or 'black_white'")
async def transformation_for_picture(base_image_id: int, body: TransformPictureModel, db: Session = Depends(get_db)):
    # current_user: User = Depends(auth_service.get_current_user),
    image_url = await repo_transform.get_picture_for_transformation(base_image_id, db)
    # current_user,
    if image_url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found")
    transform_list = create_list_transformation(body)
    url = CloudImage.get_transformed_url(image_url, transform_list)
    img = await repo_transform.set_transform_picture(base_image_id, url, db)
    return {'url': url}


# @router.post('/save/{base_picture_id}', response_model=TransformPictureResponse, status_code=status.HTTP_201_CREATED)
# async def save_transform_image(base_picture_id: int, body: SaveTransformPictureModel,
#                                db: Session = Depends(get_db)):
#     # current_user: User = Depends(auth_service.get_current_user),
#
#     img = await repo_transform.set_transform_picture(base_picture_id, body.url, db)
#     if img is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")
#     return img
