from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database.db import get_db
from api.repository.comment_service import (
    create_comment, update_comment, get_comment_by_id, delete_comment
)
from api.schemas import CommentCreate, CommentResponse

router = APIRouter()


@router.post("/comments/", response_model=CommentResponse)
async def add_comment(comment_data: CommentCreate, user_id: int, picture_id: int, db: Session = Depends(get_db)):
    comment = create_comment(db, comment_data, user_id, picture_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Picture not found")
    return comment


@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def edit_comment(comment_id: int, text: str, db: Session = Depends(get_db)):
    comment = update_comment(db, comment_id, text)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.get("/comments/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.delete("/comments/{comment_id}", response_model=CommentResponse)
async def remove_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = delete_comment(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment
