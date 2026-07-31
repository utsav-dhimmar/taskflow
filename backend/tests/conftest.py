import asyncio
import os
from collections.abc import Generator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

import app.db.models.project
import app.db.models.task
import app.db.models.user
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_hashed_password,
)
from app.db.base import Base
from app.db.main import get_session
from app.db.models.user import User
from app.main import app

TEST_DB_FILE = "./test_taskflow.db"
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_FILE}"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

TestAsyncSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


class TestEngineWrapper:
    def __init__(self, real_engine):
        self._real_engine = real_engine

    async def dispose(self):
        pass

    def __getattr__(self, attr):
        return getattr(self._real_engine, attr)


wrapped_test_engine = TestEngineWrapper(test_engine)


def run_async(coro):
    """Utility to run an async coroutine in an event loop."""
    return asyncio.run(coro)


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db_file():
    """Remove test db file if it exists at session end."""
    yield
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except OSError:
            pass


@pytest.fixture(autouse=True)
def setup_db(monkeypatch):
    """Patch DB components and recreate tables before each test."""

    async def dummy_async(*args, **kwargs):
        pass

    monkeypatch.setattr("app.db.main.engine", wrapped_test_engine)
    monkeypatch.setattr("app.db.main.async_session", TestAsyncSessionLocal)
    monkeypatch.setattr(
        "app.core.middleware.async_session", TestAsyncSessionLocal
    )

    async def _setup():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    run_async(_setup())
    yield


@pytest.fixture
def db_session() -> Generator[AsyncSession, None, None]:
    """Provide a database session for tests."""

    async def _get():
        return TestAsyncSessionLocal()

    session = run_async(_get())
    yield session
    run_async(session.close())


@pytest.fixture
def mock_celery():
    """Mock Celery send_task to prevent sending actual background tasks."""
    with patch("app.routes.auth.celery_app.send_task") as mock_send:
        yield mock_send


@pytest.fixture
def client(monkeypatch) -> Generator[TestClient, None, None]:
    """Provide a TestClient configured with the test database session."""

    async def override_get_session():
        async with TestAsyncSessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    async def dummy_async(*args, **kwargs):
        pass

    monkeypatch.setattr("app.db.main.engine", wrapped_test_engine)
    monkeypatch.setattr("app.db.main.async_session", TestAsyncSessionLocal)
    monkeypatch.setattr(
        "app.core.middleware.async_session", TestAsyncSessionLocal
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user() -> User:
    """Create and return a default test user in the database."""

    async def _create_user():
        async with TestAsyncSessionLocal() as session:
            user = User(
                email="testuser@example.com",
                password=get_hashed_password("TestPassword123!"),
                full_name="Test User",
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    return run_async(_create_user())


@pytest.fixture
def user_access_token(test_user: User) -> str:
    """Generate an access token for the test user."""
    return create_access_token(subject=test_user.id)


@pytest.fixture
def user_refresh_token(test_user: User) -> str:
    """Generate a refresh token for the test user."""
    return create_refresh_token(subject=test_user.id)
