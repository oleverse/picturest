from pathlib import Path

from fastapi import Request, APIRouter, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from starlette import status

# TODO: замінити безпосереднє звернення до бази даних на виклик API функції для отримання світлин
from api.database.db import get_db
from api.database.models import User
from api.repository.comment_service import create_comment
from api.repository.users import create_user
from api.routes.pictures import get_picture
from api.repository.pictures import get_user_pictures
from api.schemas.essential import CommentCreate, UserModel
from api.repository.web_service import get_current_user
from front.routes.web_forms import LoginForm, UserCreateForm
from api.routes import auth

router = APIRouter(tags=["web"])

template_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=template_dir)


@router.get("/", response_class=HTMLResponse)
async def root(request: Request, db: Session = Depends(get_db)):
    # pictures = await get_picture(picture_id=int, db=db)
    return templates.TemplateResponse("index.html", {
        "request": request,
        # "photos": pictures
    })


@router.get("/home")
async def home_page(request: Request, db: Session = Depends(get_db)):
    # pictures = await get_picture(picture_id=int, db=db)

    return templates.TemplateResponse("home.html", {
        "request": request,
        # "photos": pictures
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
async def add_comment(
        request: Request,
        comment_text: str = Form(...),
        user_id: int = Form(...),
        picture_id: int = Form(...),
        db: Session = Depends(get_db)
):
    comment = create_comment(comment_data=CommentCreate(text=comment_text),
                             user_id=user_id, picture_id=picture_id, db=db)
    if not comment:
        raise HTTPException(status_code=404, detail="Picture not found")

    return templates.TemplateResponse("success.html", {"request": request, "item_name": "Коментар", "item": comment})


@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            form.__dict__.update(msg="Login Successful :)")
            response = templates.TemplateResponse("home.html", form.__dict__)
            await auth.login(response=response, body=form, db=db)

            return response
        except HTTPException:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append("Incorrect Email or Password")
            return templates.TemplateResponse("login.html", form.__dict__)
    return templates.TemplateResponse("/index.html", form.__dict__)


@router.post("/register", response_class=HTMLResponse)
async def register(request: Request, db: Session = Depends(get_db)):
    form = UserCreateForm(request)
    await form.load_data()
    if await form.is_valid():

        try:
            await auth.register(body=form, db=db)
            return RedirectResponse(
                "/?msg=Successfully-Registered",
                status_code=status.HTTP_302_FOUND)  # default is post request, to use get request added status code 302
        except IntegrityError:
            form.__dict__.get("errors").append("Duplicate username or email")
            return templates.TemplateResponse("/register.html", form.__dict__)

    return templates.TemplateResponse("/home.html", form.__dict__)
