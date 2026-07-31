from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException, Request, status
from sqlalchemy import select

from app.core.security import create_access_token, create_refresh_token
from app.db.models.user import User
from app.routes.auth import get_current_user
from tests.conftest import TestAsyncSessionLocal, run_async

# ============================================================================
# Helper / Unit Tests for get_current_user
# ============================================================================


# def test_get_current_user_success():
#     mock_request = MagicMock(spec=Request)


# def test_get_current_user_success():
#     mock_request = MagicMock(spec=Request)
#     mock_user = User(
#         email="test@example.com", password="hash", full_name="Test"
#     )
#     mock_request.state.user = mock_user

#     result = run_async(get_current_user(mock_request))
#     assert result == mock_user


def test_get_current_user_unauthenticated():
    mock_request = MagicMock(spec=Request)
    mock_request.state = MagicMock(spec=[])  # no 'user' attribute on state

    with pytest.raises(HTTPException) as exc_info:
        run_async(get_current_user(mock_request))
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Not authenticated"


# ============================================================================
# POST /auth/register
# ============================================================================


def test_register_success(client, mock_celery):
    payload = {
        "email": "newregister@example.com",
        "password": "SecurePassword123!",
        "full_name": "New Register",
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["email"] == payload["email"]
    assert data["full_name"] == payload["full_name"]
    assert "id" in data
    assert "password" not in data
    assert "refresh_token" not in data

    # Verify user saved in DB
    async def _check_db():
        async with TestAsyncSessionLocal() as session:
            res = await session.execute(
                select(User).where(User.email == payload["email"])
            )
            user = res.scalars().first()
            assert user is not None
            assert user.full_name == payload["full_name"]

    run_async(_check_db())

    # Verify Celery welcome email task was sent
    mock_celery.assert_called_once_with(
        "app.worker.send_welcome_email",
        args=[payload["email"], payload["full_name"]],
    )


def test_register_duplicate_email(client, test_user):
    payload = {
        "email": test_user.email,
        "password": "Password123!",
        "full_name": "Duplicate User",
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_register_invalid_payload(client):
    # Invalid email address format
    payload = {
        "email": "not-an-email",
        "password": "short",
        "full_name": "Bad User",
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 422


# ============================================================================
# POST /auth/login
# ============================================================================


def test_login_success(client, test_user, mock_celery):
    payload = {
        "email": test_user.email,
        "password": "TestPassword123!",
    }
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name
    assert "password" not in data

    # Verify cookies
    cookies = response.cookies
    assert "access_token" in cookies
    assert "refresh_token" in cookies

    # Verify refresh_token & expires_at in DB
    async def _check_db():
        async with TestAsyncSessionLocal() as session:
            db_user = await session.get(User, test_user.id)
            assert db_user.refresh_token == cookies["refresh_token"]
            assert db_user.expires_at is not None

    run_async(_check_db())

    # Verify login email task triggered
    mock_celery.assert_called_once_with(
        "app.worker.send_login_email",
        args=[{"full_name": test_user.full_name, "email": test_user.email}],
    )


def test_login_incorrect_password(client, test_user):
    payload = {
        "email": test_user.email,
        "password": "WrongPassword!",
    }
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_login_nonexistent_user(client):
    payload = {
        "email": "nobody@example.com",
        "password": "SomePassword123!",
    }
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_login_celery_task_failure_does_not_break_login(
    client, test_user, mock_celery
):
    mock_celery.side_effect = Exception("Redis connection failed")

    payload = {
        "email": test_user.email,
        "password": "TestPassword123!",
    }
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 200
    assert "access_token" in response.cookies


# ============================================================================
# POST /auth/refresh
# ============================================================================


def test_refresh_token_success(client, test_user):
    # Set valid refresh token for user in DB
    refresh_token = create_refresh_token(subject=test_user.id)
    expires_at = datetime.now(tz=UTC) + timedelta(days=7)

    async def _setup_token():
        async with TestAsyncSessionLocal() as session:
            user = await session.get(User, test_user.id)
            user.refresh_token = refresh_token
            user.expires_at = expires_at
            session.add(user)
            await session.commit()

    run_async(_setup_token())

    client.cookies.set("refresh_token", refresh_token)
    response = client.post("/auth/refresh")
    assert response.status_code == 200

    data = response.json()
    assert data["email"] == test_user.email

    # Check new cookies are set
    cookies = response.cookies
    assert "access_token" in cookies
    assert "refresh_token" in cookies

    # Verify updated refresh_token in DB
    async def _check_db():
        async with TestAsyncSessionLocal() as session:
            user = await session.get(User, test_user.id)
            assert user.refresh_token == cookies["refresh_token"]

    run_async(_check_db())


def test_refresh_token_missing_cookie(client):
    response = client.post("/auth/refresh")
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_refresh_token_invalid_jwt(client):
    client.cookies.set("refresh_token", "invalid.jwt.token")
    response = client.post("/auth/refresh")
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_refresh_token_access_token_provided(client, test_user):
    # Access tokens lack {"refresh": True} payload claim
    access_token = create_access_token(subject=test_user.id)
    client.cookies.set("refresh_token", access_token)
    response = client.post("/auth/refresh")
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_refresh_token_mismatched_db_token(client, test_user):
    refresh_token = create_refresh_token(subject=test_user.id)

    async def _setup_mismatch():
        async with TestAsyncSessionLocal() as session:
            user = await session.get(User, test_user.id)
            user.refresh_token = "different_token_in_db"
            user.expires_at = datetime.now(tz=UTC) + timedelta(days=7)
            session.add(user)
            await session.commit()

    run_async(_setup_mismatch())

    client.cookies.set("refresh_token", refresh_token)
    response = client.post("/auth/refresh")
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_refresh_token_user_not_found(client):
    random_uuid = str(uuid4())
    fake_refresh_token = create_refresh_token(subject=random_uuid)
    client.cookies.set("refresh_token", fake_refresh_token)
    response = client.post("/auth/refresh")
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_refresh_token_expired_in_db(client, test_user):
    refresh_token = create_refresh_token(subject=test_user.id)
    expired_time = datetime.now(tz=UTC) - timedelta(days=1)

    async def _setup_expired():
        async with TestAsyncSessionLocal() as session:
            user = await session.get(User, test_user.id)
            user.refresh_token = refresh_token
            user.expires_at = expired_time
            session.add(user)
            await session.commit()

    run_async(_setup_expired())

    client.cookies.set("refresh_token", refresh_token)
    response = client.post("/auth/refresh")
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


# ============================================================================
# POST /auth/logout
# ============================================================================


def test_logout_success(client, test_user, user_access_token):
    # Setup initial refresh_token in DB
    refresh_token = create_refresh_token(subject=test_user.id)

    async def _setup_logout_user():
        async with TestAsyncSessionLocal() as session:
            user = await session.get(User, test_user.id)
            user.refresh_token = refresh_token
            session.add(user)
            await session.commit()

    run_async(_setup_logout_user())

    client.cookies.set("access_token", user_access_token)
    response = client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json() == {"message": "Successfully logged out"}

    # Verify refresh_token cleared in DB
    async def _check_db():
        async with TestAsyncSessionLocal() as session:
            user = await session.get(User, test_user.id)
            assert user.refresh_token is None

    run_async(_check_db())


def test_logout_unauthenticated(client):
    response = client.post("/auth/logout")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


# ============================================================================
# GET /auth/me
# ============================================================================


def test_get_me_success_cookie(client, test_user, user_access_token):
    client.cookies.set("access_token", user_access_token)
    response = client.get("/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name
    assert data["id"] == str(test_user.id)


def test_get_me_success_bearer_header(client, test_user, user_access_token):
    headers = {"Authorization": f"Bearer {user_access_token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email


def test_get_me_unauthenticated(client):
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_me_invalid_token(client):
    client.cookies.set("access_token", "invalid_access_token")
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


def test_get_me_user_not_found(client):
    non_existent_id = str(uuid4())
    token = create_access_token(subject=non_existent_id)
    client.cookies.set("access_token", token)
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "User not found"


def test_get_me_session_expired(client, test_user):
    token = create_access_token(subject=test_user.id)
    expired_time = datetime.now(UTC) - timedelta(minutes=10)

    async def _setup_expired():
        async with TestAsyncSessionLocal() as session:
            user = await session.get(User, test_user.id)
            user.expires_at = expired_time
            session.add(user)
            await session.commit()

    run_async(_setup_expired())

    client.cookies.set("access_token", token)
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Session expired"
