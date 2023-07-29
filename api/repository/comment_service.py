from typing import Type
from fastapi import HTTPException
from sqlalchemy.orm import Session
from api.database.models import Comment
from api.schemas.essential import CommentCreate
from datetime import datetime
from api.repository.users import user_exists


async def create_comment(db: Session, comment_data: CommentCreate, user_id: int):
    if await user_exists(user_id, db):
        comment = Comment(**comment_data.model_dump(), user_id=user_id)
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment
    raise HTTPException(status_code=404, detail="User not found")


async def update_comment(db: Session, comment_data: CommentCreate, comment_id: int, user_id: int):
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.user_id == user_id).first()
    if not comment:
        return None
    comment.text = comment_data.text
    comment.edited = True
    comment.edited_at = datetime.now()
    db.commit()
    db.refresh(comment)
    return comment


async def delete_comment_by_id(db: Session, comment_id: int, user_id: int):
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.user_id == user_id).first()
    if not comment:
        return None
    db.delete(comment)
    db.commit()
    return comment


async def get_comment_by_id(db: Session, comment_id: int):
    return db.query(Comment).filter(Comment.id == comment_id).first()


async def delete_comment(db: Session, comment_id: int):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment:
        db.delete(comment)
        db.commit()
        return comment
    return None


async def get_comments_by_picture_id(db: Session, picture_id: int) -> list[Type[Comment]]:
    return db.query(Comment).filter(Comment.picture_id == picture_id).all()
