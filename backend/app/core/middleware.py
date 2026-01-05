from datetime import datetime
from typing import List, Optional
from uuid import UUID

import jwt
from fastapi import Request, status
from fastapi.responses import JSONResponse
from jwt.exceptions import InvalidTokenError
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import setting
from app.db.main import async_session
from app.models.user import User


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        exclude_paths: Optional[List[str]] = None,
    ):
        super().__init__(app)
        self.exclude_paths = exclude_paths or []

    async def dispatch(self, request: Request, call_next):
        # Check if path is excluded
        # Simple exact match or startswith for now?
        # Let's support simple exact match and "startswith" for checking sub-paths if needed.
        # But list of specific exclusion is safer.
        path = request.url.path

        # Static exclusions
        if path in self.exclude_paths:
            return await call_next(request)

        # Regex or prefix exclusions (e.g. /docs, /openapi.json)
        # We can add them to exclude_paths too, but let's handle docs explicitly if not passed
        if (
            path.startswith("/docs")
            or path.startswith("/redoc")
            or path == "/openapi.json"
            or path == ""
        ):
            return await call_next(request)

        # Token Extraction
        token = request.cookies.get("access_token")
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Not authenticated"},
            )
        print(f"{token=}")
        try:
            payload = jwt.decode(
                token, setting.SECRET_KEY, algorithms=[setting.ALGORITHM]
            )
            print(f"{payload=}")
            user_id: str = payload.get("sub")
            print(f"{user_id=}")
            if user_id is None:
                raise InvalidTokenError()
        except InvalidTokenError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid token"},
            )

        # Database Check
        # We process this in a new session scope
        async with async_session() as session:
            user = await session.get(User, UUID(user_id))
            if not user:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "User not found"},
                )

            # Check Expiration/Validity from DB side
            if user.expires_at and user.expires_at < datetime.utcnow():
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Session expired"},
                )

            # Attach user to request state
            request.state.user = user

            # We don't return the session, so user object is detached after this block.
            # This is fine for reading properties.
            # If routes need to modify user, they should merge it into their own session dependencies.

        response = await call_next(request)
        return response
