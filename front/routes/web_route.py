from pathlib import Path
from fastapi import Request, APIRouter, Form, HTTPException, Depends, UploadFile, File, Header
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from starlette import status
# TODO: замінити безпосереднє звернення до бази даних на виклик API функції для отримання світлин
from api.database.db import get_db
from api.database.models import User, Picture, Tag
from api.repository.comment_service import create_comment
from api.repository.pictures import get_user_pictures, get_all_pictures
from api.schemas.essential import CommentCreate
from api.services.auth import auth_service
from api.repository.users import add_to_blacklist
from front.routes.web_forms import LoginForm, UserCreateForm
from api.routes import auth, pictures, comments

router = APIRouter(tags=["web"])

template_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=template_dir)


@router.get("/", response_class=HTMLResponse)
async def root(request: Request, db: Session = Depends(get_db)):
    pictures = get_all_pictures(limit=5, offset=0, db=db)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "photos": pictures
    })


@router.get("/authorized", response_class=HTMLResponse)
async def home_page(request: Request, user_id: int = 1, db: Session = Depends(get_db)):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Немає токену автентифікації")

    pictures = get_all_pictures(limit=5, offset=0, db=db)
    pictures_user = await get_user_pictures(user_id=user_id, db=db)
    response = templates.TemplateResponse("authorized.html", {
        "request": request,
        "photos_user": pictures_user,
        "photos": pictures
    })
    return response


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@router.post("/add_comment", response_class=HTMLResponse)
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
async def login(request: Request, user_id: int = 1, db: Session = Depends(get_db)):
    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            form.__dict__.update(msg="Login Successful :)")
            response = RedirectResponse("/authorized?msg=Логін%20виконаний%20успішно!",
                                        status_code=status.HTTP_302_FOUND,
                                        headers={"Location": f"/authorized?user_id={user_id}"})

            access_token = auth_service.create_access_token(data={"sub": user_id})
            response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
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

    return templates.TemplateResponse("/authorized.html", form.__dict__)


@router.post("/upload")
async def upload_photo_view(request: Request,
                            file: UploadFile = File(...),
                            db: Session = Depends(get_db)
                            ):
    user = await auth.auth_service.get_current_user(token=request.cookies["access_token"][7:], db=db)

    await pictures.create_picture(description="Some description", file=file, tags=['1'], db=db,
                                  current_user=user)

    return RedirectResponse("/authorized?msg=Фото%20завантажено%20успішно!", status_code=status.HTTP_302_FOUND,
                            headers={"Location": f"/authorized?user_id={user.id}"})


@router.post("/logout_user")
async def logout_user(request: Request, db: Session = Depends(get_db)):
    access_token = request.cookies.get("access_token")
    print(access_token)
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    await add_to_blacklist(access_token[7:], db)
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    response.delete_cookie("access_token")
    return response
