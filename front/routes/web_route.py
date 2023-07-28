from pathlib import Path

from fastapi import Request, APIRouter, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

# TODO: замінити безпосереднє звернення до бази даних на виклик API функції для отримання світлин
from api.database.db import get_db
from api.repository.comment_service import create_comment
from api.repository.pictures import get_user_pictures
from api.schemas.essential import CommentCreate

template_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=template_dir)

router = APIRouter(tags=["web"])


@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    # TODO: замінити безпосереднє звернення до бази даних на виклик API функції для отримання світлин
    pictures = await get_user_pictures(user_id=1, db=db)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "photos": pictures
    })


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/upload-picture", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@router.post("/add_comment/", response_class=HTMLResponse)
async def add_comment(request: Request, comment_text: str = Form(), user_id: int = Form(), picture_id: int = Form(),
                      db: Session = Depends(get_db)):
    comment = create_comment(comment_data=CommentCreate(text=comment_text),
                             user_id=user_id, picture_id=picture_id, db=db)
    if not comment:
        raise HTTPException(status_code=404, detail="Picture not found")

    return templates.TemplateResponse("success.html", {"request": request, "item_name": "Коментар", "item": comment})
