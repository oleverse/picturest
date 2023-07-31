from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request, Response
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from api.database.db import get_db
from api.database.models import User, RoleNames
from api.repository import users as repository_users
from api.schemas.essential import RequestEmail, UserStatusResponse, UserStatusChange
from api.schemas.essential import UserModel, UserResponse, TokenModel
from api.services.auth import auth_service
from api.services.email import send_confirmation_email


router = APIRouter(prefix='/auth', tags=['auth'])
security = HTTPBearer()


@router.post('/register', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(body: UserModel, request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Account already exists')

    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    access_token = await auth_service.create_access_token(data={'sub': body.email})
    refresh_token = await auth_service.create_refresh_token(data={'sub': body.email})
    background_tasks.add_task(send_confirmation_email, new_user.email, new_user.username, str(request.base_url))
    return {'user': new_user, "access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer",
            'detail': 'User successfully created'}


@router.post('/login', response_model=TokenModel)
async def login(response: Response, body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect login or password')
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Email not confirmed')
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='The user is deactivated.')
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect login or password')

    access_token = await auth_service.create_access_token(data={'sub': user.email})

    refresh_token = await auth_service.create_refresh_token(data={'sub': user.email})

    await repository_users.update_token(user, refresh_token, db)

    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_tokens(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')
    access_token = await auth_service.create_access_token(data={'sub': email})
    refresh_token = await auth_service.create_refresh_token(data={'sub': email})
    await repository_users.update_token(user, refresh_token, db)
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


@router.get('/confirm_email/{token}')
async def confirm_email(token: str, db: Session = Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Verification error')
    if user.confirmed:
        return {'message': 'Your email is already confirmed'}
    await repository_users.confirm_email(email, db)
    return {'message': 'Email confirmed'}


@router.post('/request_email_confirmation')
async def request_email_confirmation(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                                     db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.email, db)
    if user.confirmed:
        return {'message': 'Your email is already confirmed'}
    if user:
        background_tasks.add_task(send_confirmation_email, user.email, user.username, str(request.base_url))
    return {'message': 'Check your email for confirmation.'}


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Security(security),
                 db: Session = Depends(get_db)):
    token = credentials.credentials

    await repository_users.add_to_blacklist(token, db)
    return {"message": 'User has been logged out.'}


@router.put("/users/deactivate", response_model=UserStatusResponse)
async def user_deactivate(user_data: UserStatusChange, current_user: User = Depends(auth_service.get_current_user),
                          db: Session = Depends(get_db)):
    if current_user.role.name != RoleNames.admin.name:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only administrators can deactivate users!")

    user = await repository_users.ban_user(user_data.email, current_user.id, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")

    return user


@router.put("/users/activate", response_model=UserStatusResponse)
async def user_activate(user_data: UserStatusChange, current_user: User = Depends(auth_service.get_current_user),
                        db: Session = Depends(get_db)):
    if current_user.role.name != RoleNames.admin.name:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only administrators can activate users!")
    user = await repository_users.ban_user(user_data.email, current_user.id, db, is_active=True)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")

    return user
