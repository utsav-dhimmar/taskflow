from datetime import datetime, timedelta
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from jwt.exceptions import InvalidTokenError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import setting
from app.core.security import create_access_token, create_refresh_token
from app.db.main import get_session
from app.models.user import User
from app.schema.auth import (
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services.user_service import UserService
from app.worker import send_login_email, send_welcome_email

router = APIRouter(prefix="/auth", tags=["auth"])
user_service = UserService()


async def get_current_user(
    request: Request,
) -> User:
    # user is injected by auth middleware
    # if no then can't access
    if not hasattr(request.state, "user"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return request.state.user


@router.post("/register", response_model=UserResponse)
async def register(
    user_create: UserCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Register a new user controller
    """
    user = await user_service.create_user(session, user_create)
    send_welcome_email.delay(user.email, user.full_name)
    return user


@router.post("/login", response_model=UserResponse)
async def login(
    user_login: UserLogin,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Login a user controller
    """

    user = await user_service.login(session, user_login)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)

    # Store refresh token and expiration in DB
    user.refresh_token = refresh_token
    user.expires_at = datetime.utcnow() + timedelta(
        days=setting.REFRESH_TOKEN_EXPIRE_DAYS
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)
    try:
        send_login_email.delay({"full_name": user.full_name, "email": user.email})
    except Exception as e:
        print("mail send failed ")
        print(e)
    json_user_data = jsonable_encoder(user, exclude={"password", "refresh_token"})
    res = JSONResponse(
        content=json_user_data,
        media_type="application/json",
    )
    res.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=False,  # temp
        samesite="lax",
        max_age=setting.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    res.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",  # temp
        max_age=setting.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return res


@router.post("/refresh", response_model=UserResponse)
async def refresh_token_endpoint(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Refresh a user the access token
    """
    # 1. get the refresh token  No ? not allow
    # 2. decode the refresh token invalid ? no
    # 3. get the user by id , coudnt' find ? No
    # 4. check db refresh token and expiration Invalid or expired > No
    # 5. create another the refresh token and also update in db
    refresh_token = request.cookies.get("refresh_token")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        # headers={"WWW-Authenticate": "Bearer"},
    )
    if not refresh_token:
        raise credentials_exception

    try:
        payload = jwt.decode(
            refresh_token, setting.SECRET_KEY, algorithms=[setting.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        is_refresh: bool = payload.get("refresh")
        if user_id is None or not is_refresh:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    user = await user_service.get_user_by_id(session, user_id)
    if user is None or user.refresh_token != refresh_token:
        raise credentials_exception

    # Check DB expiration
    if user.expires_at and user.expires_at < datetime.utcnow():
        raise credentials_exception

    # new tokens
    new_access_token = create_access_token(subject=user.id)
    new_refresh_token = create_refresh_token(subject=user.id)

    user.refresh_token = new_refresh_token
    user.expires_at = datetime.utcnow() + timedelta(
        days=setting.REFRESH_TOKEN_EXPIRE_DAYS
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    #  add in cookie
    json_user_data = jsonable_encoder(user, exclude={"password", "refresh_token"})
    res = JSONResponse(
        content=json_user_data,
        media_type="application/json",
    )
    res.set_cookie(
        "access_token",
        new_access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=setting.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    res.set_cookie(
        "refresh_token",
        new_refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=setting.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return res


@router.post("/logout")
async def logout(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    # remove the refresh token from db
    # remove the cookies

    current_user.refresh_token = None
    session.add(current_user)
    await session.commit()

    res = JSONResponse(content={"message": "Successfully logged out"})
    res.delete_cookie("access_token")
    res.delete_cookie("refresh_token")
    return res


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    # return the current user
    return current_user
