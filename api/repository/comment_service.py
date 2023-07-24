from sqlalchemy.orm import Session
from api.database.models import Comment
from api.schemas import CommentCreate
from datetime import datetime


def create_comment(db: Session, comment_data: CommentCreate, user_id: int, picture_id: int):
    comment = Comment(**comment_data.dict(), user_id=user_id, picture_id=picture_id, created_at=datetime.now())
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def update_comment(db: Session, comment_id: int, text: str):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        return None
    comment.text = text
    comment.edited = True
    comment.edited_at = datetime.now()
    db.commit()
    db.refresh(comment)
    return comment


def get_comment_by_id(db: Session, comment_id: int):
    return db.query(Comment).filter(Comment.id == comment_id).first()


def delete_comment(db: Session, comment_id: int):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        return None
    db.delete(comment)
    db.commit()
    return comment
