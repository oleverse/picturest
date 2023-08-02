from typing import Type
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import api.repository.pictures as pict_repo
from api.database.models import Comment, User
from api.schemas.essential import CommentCreate, CommentBase
from datetime import datetime


async def create_comment(db: Session, comment_data: CommentCreate, user: User):
    picture = await pict_repo.get_picture(comment_data.picture_id, db)
    if not picture:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Picture not found.")
    if not user.role.can_post_own_comment:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not allowed to leave comments!")
    comment = Comment(**comment_data.model_dump(), user_id=user.id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


async def update_comment(db: Session, comment_data: CommentBase, comment_id: int, user: User):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        return None
    picture = await pict_repo.get_picture(comment.picture_id, db)
    if not picture:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Picture not found.")
    if comment.user_id != user.id and not user.role.can_mod_not_own_comment:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not allowed to edit another person's comments!")
    if not user.role.can_mod_own_comment:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not allowed to edit your comments!")
    comment.text = comment_data.text
    comment.edited = True
    comment.edited_at = datetime.now()
    db.commit()
    db.refresh(comment)
    return comment


async def delete_comment_by_id(db: Session, comment_id: int, user: User):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        return None
    if comment.user_id != user.id and not user.role.can_del_not_own_comment:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Deleting another person's comments is forbidden!")
    if not user.role.can_del_own_comment:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not allowed to delete your comments!")
    db.delete(comment)
    db.commit()
    return comment


async def get_comment_by_id(db: Session, comment_id: int):
    return db.query(Comment).filter(Comment.id == comment_id).first()


async def get_comments_by_picture_id(db: Session, picture_id: int) -> list[Type[Comment]]:
    return db.query(Comment).filter(Comment.picture_id == picture_id).all()
