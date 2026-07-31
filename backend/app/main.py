from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.logging import get_logger
from app.core.middleware import AuthMiddleware
from app.db.main import engine
from app.routes.auth import router as auth_router
from app.routes.project import router as project_router
from app.routes.task import router as task_router
from app.routes.user import router as user_router
from app.schemas.error import ErrorResponse

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Checking database connection...")
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connected successfully!")
    except SQLAlchemyError as e:
        logger.error(f"Database connection failed: {e}")

    yield

    logger.info("Shutting down database engine...")
    try:
        await engine.dispose()
    except SQLAlchemyError as e:
        logger.error(f"Failed to cleanly dispose database engine: {e}")


app = FastAPI(
    title="TaskFlow API",
    lifespan=lifespan,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=bool(settings.DEBUG),
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """

    This is a global exception handler for all exceptions that are not caught by other handlers.

    """

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error",
            message="An unexpected error occurred",
        ).model_dump(),
    )


app.add_middleware(
    AuthMiddleware,
    # no auth require for these paths
    exclude_paths=[
        "/",
        "/auth/login",
        "/auth/register",
        "/auth/refresh",
        "/scalar-docs",
        str(app.openapi_url),
        str(app.docs_url),
        str(app.redoc_url),
    ],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_URLS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    auth_router,
    tags=["auth"],
)
app.include_router(
    user_router,
    tags=["users"],
)
app.include_router(
    project_router,
    tags=["projects"],
)
app.include_router(
    task_router,
    tags=["tasks"],
)


@app.get("/scalar-docs", include_in_schema=False)
async def scalar_html():
    from scalar_fastapi import get_scalar_api_reference

    return get_scalar_api_reference(
        title=app.title,
        dark_mode=True,
        openapi_url=str(app.openapi_url),
    )
