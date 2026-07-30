from datetime import UTC, datetime
from uuid import UUID

import jwt
from fastapi import Request, status
from fastapi.responses import JSONResponse
from jwt.exceptions import InvalidTokenError
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logging import get_logger
from app.db.main import async_session
from app.models.user import User

logger = get_logger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        exclude_paths: list[str] | None = None,
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
            path.startswith(("/docs", "/redoc"))
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
        logger.debug(f"Token received: {token[:20]}...")
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            logger.debug(f"Payload decoded: {payload}")
            user_id: str | None = payload.get("sub")
            logger.debug(f"User ID from token: {user_id}")
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
            if user.expires_at:
                expires_at = (
                    user.expires_at.replace(tzinfo=UTC)
                    if user.expires_at.tzinfo is None
                    else user.expires_at
                )
                if expires_at < datetime.now(tz=UTC):
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
