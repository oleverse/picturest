from fastapi.templating import Jinja2Templates
from fastapi import Request, APIRouter, Form, HTTPException
from fastapi.responses import HTMLResponse

# TODO: замінити безпосереднє звернення до бази даних на виклик API функції для отримання світлин
from api.database.db import get_db
from api.repository.pictures import get_user_pictures
from api.repository.comment_service import create_comment
from api.schemas import CommentCreate


templates = Jinja2Templates(directory="templates")

router = APIRouter(tags=["web"])


@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # TODO: замінити безпосереднє звернення до бази даних на виклик API функції для отримання світлин
    pictures = await get_user_pictures(user_id=1, db=get_db())
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
async def add_comment(request: Request, comment_text: str = Form(), user_id: int = Form(), picture_id: int = Form()):
    comment = create_comment(comment_data=CommentCreate(text=comment_text),
                             user_id=user_id, picture_id=picture_id, db=get_db())
    if not comment:
        raise HTTPException(status_code=404, detail="Picture not found")

    return templates.TemplateResponse("success.html", {"request": request, "item_name": "Коментар", "item": comment})

