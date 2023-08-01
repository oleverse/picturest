from pathlib import Path
from re import split as re_split

from fastapi import Request, APIRouter, Form, HTTPException, Depends, UploadFile, File, status, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session

from api.database.db import get_db
from api.database.models import User
from api.repository.comments import create_comment
from api.repository.pictures import get_user_pictures, get_all_pictures
from api.repository.users import add_to_blacklist
from api.routes import auth as auth_route, pictures
from api.schemas.essential import CommentCreate, UserModel
from api.services.auth import auth_service
from front.routes.web_forms import LoginForm, UserCreateForm


router = APIRouter(tags=["web"])

template_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=template_dir)


async def get_user_token(request: Request) -> str:
    if request and "access_token" in request.cookies:
        return request.cookies["access_token"].split()[1].strip()


async def get_logged_in_user(request: Request, db: Session) -> User:
    access_token = await get_user_token(request)
    try:
        logged_in_user = await auth_service.get_current_user(access_token, db)
    except AttributeError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad access token!")
    else:
        return logged_in_user


@router.get("/", response_class=HTMLResponse)
async def root(request: Request, db: Session = Depends(get_db)):
    all_pictures = await get_all_pictures(limit=5, offset=0, db=db)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "photos": all_pictures
    })


@router.get("/authorized", response_class=HTMLResponse)
async def home_page(request: Request, db: Session = Depends(get_db)):
    logged_in_user = await get_logged_in_user(request, db)

    all_pictures = await get_all_pictures(limit=5, offset=0, db=db)
    pictures_user = await get_user_pictures(user_id=logged_in_user.id, db=db)
    response = templates.TemplateResponse("authorized.html", {
        "request": request,
        "photos_user": pictures_user,
        "photos": all_pictures
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
        picture_id: int = Form(...),
        db: Session = Depends(get_db)
):
    logged_in_user = await get_logged_in_user(request, db)
    comment = await create_comment(comment_data=CommentCreate(text=comment_text, picture_id=picture_id),
                                   user=logged_in_user, db=db)

    if not comment:
        raise HTTPException(status_code=404, detail="Picture not found")

    return templates.TemplateResponse("success.html", {"request": request,
                                                       "item_name": "Коментар", "item": comment.text})


@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            response = RedirectResponse("/authorized",
                                        status_code=status.HTTP_302_FOUND)
            login_result = await auth_route.login(response=response, body=form, db=db)
            form.__dict__.update(msg="Login Successful :)")

            logged_in_user = await auth_service.get_current_user(login_result["access_token"], db)
            response.headers["location"] = f"/authorized?user_id={logged_in_user.id}"

            return response
        except HTTPException as http_ex:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append(http_ex.detail)
            return templates.TemplateResponse("login.html", form.__dict__)
    return templates.TemplateResponse("/index.html", form.__dict__)


@router.post("/register", response_class=HTMLResponse)
async def register(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    form = UserCreateForm(request)
    await form.load_data()
    if await form.is_valid():

        try:
            await auth_route.register(request=request,
                                      background_tasks=background_tasks,
                                      body=UserModel(username=form.username, email=form.email, password=form.password),
                                      db=db)
            return RedirectResponse(
                "/?msg=Successfully-Registered",
                status_code=status.HTTP_302_FOUND)  # default is post request, to use get request added status code 302
        except IntegrityError:
            form.__dict__.get("errors").append("Duplicate username or email")
            return templates.TemplateResponse("/register.html", form.__dict__)

    return templates.TemplateResponse("/authorized.html", form.__dict__)


@router.post("/upload")
async def upload_photo_view(request: Request,
                            description: str = Form(),
                            tags: str = Form(''),
                            file: UploadFile = File(...),
                            db: Session = Depends(get_db)
                            ):
    try:
        logged_in_user = await get_logged_in_user(request, db)

        tags_list = [tag_name.strip() for tag_name in re_split(r'@\s+,\s+', tags)]
        await pictures.create_picture(description=description, file=file, tags=tags_list,
                                      db=db, current_user=logged_in_user)

        return RedirectResponse("/authorized", status_code=status.HTTP_302_FOUND,
                                headers={"Location": f"/authorized?user_id={logged_in_user.id}"})
    except HTTPException as http_ex:
        if http_ex.status_code == status.HTTP_401_UNAUTHORIZED:
            return templates.TemplateResponse("/fail.html", {
                "request": request,
                "error": "Не вдалося визначити користувача!"})
        raise http_ex


@router.get("/logout_user")
async def logout_user(request: Request, db: Session = Depends(get_db)):
    access_token = await get_user_token(request)
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    await add_to_blacklist(access_token, db)
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    response.delete_cookie("access_token")

    return response
