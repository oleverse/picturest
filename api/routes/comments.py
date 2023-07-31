from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.database.db import get_db
from api.database.models import User
from api.repository.comments import create_comment, update_comment, delete_comment_by_id, get_comment_by_id
from api.schemas.essential import CommentCreate, CommentResponse, CommentBase
from api.services.auth import auth_service


router = APIRouter(prefix='/comments', tags=["comments"])


@router.post("/", response_model=CommentResponse)
async def add_comment(comment_data: CommentCreate, db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    """
    The add_comment function creates a new comment for the picture with the given id.

    :param comment_data: CommentCreate: Get the data from the request body
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the user that is currently logged in
    :return: A comment object
    """
    comment = await create_comment(db, comment_data, current_user)
    if not comment:
        raise HTTPException(status_code=404, detail="Picture not found")
    return comment


@router.put("/{comment_id}", response_model=CommentResponse)
async def edit_comment(
        comment_data: CommentBase,
        comment_id: int,
        user=Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)):
    """
    The edit_comment function is used to edit a comment.

    :param comment_data:  CommentCreate object containing the new data for the comment
    :param comment_id: int: Specify the comment that is being edited
    :param user: Check if the user is authorized to edit a comment
    :param db: Session: Get the database session
    :return: A CommentCreate object
    """
    comment = await update_comment(db, comment_data, comment_id, user)

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.delete("/{comment_id}", response_model=CommentResponse)
async def delete_comment(
        comment_id: int,
        current_user=Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)):
    """
    The delete_comment function deletes a comment by its ID.

    :param comment_id: int: Specify the id of the comment to delete
    :param current_user: Get the user who is currently logged in
    :param db: Session: Get the database session
    :return: The deleted comment
    """
    comment = await delete_comment_by_id(db, comment_id, current_user)

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    # if current_user.role.name not in [Role.admin, Role.moderator]:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                         detail="You don't have permission to delete comments")
    return comment


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: int, db: Session = Depends(get_db)):
    """
    The get_comment function takes a comment_id and returns the Comment object with that id.
    If no such comment exists, it raises an HTTPException with status code 404.

    :param comment_id: int: Get the comment id from the url
    :param db: Session: Pass the database session to the function
    :return: A comment object
    """
    comment = await get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment
