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
    comment = await create_comment(db, comment_data, current_user)
    if not comment:
        raise HTTPException(status_code=404, detail="Picture not found")
    return comment


@router.put("/{comment_id}", response_model=CommentResponse)
async def edit_comment(
        comment_data: CommentBase,
        comment_id: int,
        user=Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    comment = await update_comment(db, comment_data, comment_id, user)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.delete("/{comment_id}", response_model=CommentResponse)
async def delete_comment(
        comment_id: int,
        current_user=Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    comment = await delete_comment_by_id(db, comment_id, current_user)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    # if current_user.role.name not in [Role.admin, Role.moderator]:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                         detail="You don't have permission to delete comments")
    return comment


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = await get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment
