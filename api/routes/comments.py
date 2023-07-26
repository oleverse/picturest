from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.database.db import get_db
from api.database.models import Role, User
from api.repository.comment_service import (
    create_comment, update_comment, delete_comment_by_id, get_comment_by_id
)
from api.schemas import CommentCreate, CommentResponse

from api.services.auth import Auth

router = APIRouter(prefix='/comments', tags=["comments"])
auth_service = Auth()


@router.post("/", response_model=CommentResponse)
async def add_comment(comment_data: CommentCreate, user_id: int, picture_id: int, db: Session = Depends(get_db)):
    comment = create_comment(db, comment_data, user_id, picture_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Picture not found")
    return comment


@router.put("/{comment_id}", response_model=CommentResponse)
async def edit_comment(
        comment_id: int,
        text: str,
        user=Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    comment = update_comment(db, comment_id, text, user.id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.delete("/{comment_id}", response_model=CommentResponse)
async def delete_comment(
        comment_id: int,
        user=Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    comment = delete_comment_by_id(db, comment_id, user.id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.delete("/{comment_id}/user", response_model=CommentResponse)
async def delete_comment_by_user(
        comment_id: int,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    comment = get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if current_user.role.name not in [Role.admin, Role.moderator]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You don't have permission to delete comments")
    return delete_comment(get_db(), comment_id)

