from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from scalar_fastapi import get_scalar_api_reference

from app.core.config import setting
from app.core.constants import API_PREFIX
from app.core.middleware import AuthMiddleware
from app.db.main import engine, init_db
from app.routes.auth import router as auth_router
from app.routes.project import router as project_router
from app.routes.task import router as task_router
from app.routes.user import router as user_router


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
    openapi_url=f"{API_PREFIX}/openapi.json",
    docs_url=f"{API_PREFIX}/docs",
    redoc_url=f"{API_PREFIX}/redoc",
    debug=True if setting.DEBUG else False,
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "path": request.url.path},
    )


app.add_middleware(
    AuthMiddleware,  # ty:ignore[invalid-argument-type]
    # no auth require for these paths
    exclude_paths=[
        "/auth/login",
        "/auth/register",
        "/auth/refresh",
        "/api/scalar",
        str(app.openapi_url),
        str(app.docs_url),
        str(app.redoc_url),
    ],
)


app.add_middleware(
    CORSMiddleware,  # ty:ignore[invalid-argument-type]
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


@app.get(f"{API_PREFIX}/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
        dark_mode=True,
    )
