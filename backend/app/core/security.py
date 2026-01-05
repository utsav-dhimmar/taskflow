from datetime import datetime, timedelta
from typing import Any, Union

import jwt
from passlib.context import CryptContext

from app.core.config import setting

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    """
    Generate a hashed password
    """
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a hashed password
    """
    return pwd_context.verify(password, hashed_password)


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta | None = None
) -> str:
    """
    Create an access token
    - short lived token use for accessing the apis
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, setting.SECRET_KEY, algorithm=setting.ALGORITHM)


def create_refresh_token(subject: Union[str, Any]) -> str:
    """
    Create a refresh token
    - long lived token use for refreshing the access token
    """

    expire = datetime.utcnow() + timedelta(days=setting.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "refresh": True}
    return jwt.encode(to_encode, setting.SECRET_KEY, algorithm=setting.ALGORITHM)
