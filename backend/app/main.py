from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import setting
from app.core.middleware import AuthMiddleware
from app.db.main import engine, init_db
from app.routes.auth import router as auth_router
from app.routes.project import router as project_router
from app.routes.task import router as task_router
from app.routes.user import router as user_router
from app.schemas.error import ErrorResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("start")
    await init_db()
    yield
    await engine.dispose()
    print("end")


app = FastAPI(
    title="TaskFlow API",
    lifespan=lifespan,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=bool(setting.DEBUG),
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "path": request.url.path},
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
    allow_origins=setting.FRONTEND_URLS,
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
    )
