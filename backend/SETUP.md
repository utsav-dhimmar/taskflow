# TaskFlow Backend Setup Guide

## Prerequisites

- **Python 3.12+**
- **uv** (recommended) or pip
- **Docker & Docker Compose** (for local development with PostgreSQL, Redis, Mailhog)
- **PostgreSQL 16+** (if running without Docker)

---

## Quick Start (Docker Compose - Recommended)

### 1. Clone and navigate to backend

```bash
cd backend
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start services with Docker Compose

```bash
docker-compose up -d
```

This starts:

- **PostgreSQL** on port 5432
- **Redis** on port 6379
- **Mailhog** (SMTP: 1025, UI: 8025)
- **FastAPI app** on port 8000 (with hot reload)

### 4. Verify services

```bash
# Check API docs
open http://localhost:8000/docs

# Use scalar docs
open http://localhost:8000/scalar-docs

# Check Mailhog UI
open http://localhost:8025
```

---

## Manual Setup (Without Docker)

### 1. Install dependencies

```bash
# Using uv (recommended)
uv sync

# Or with pip
pip install -e .
```

### 2. Set up PostgreSQL

```bash
# Create database
createdb taskflow

# Or with psql
psql -c "CREATE DATABASE taskflow;"
```

### 3. Set up Redis

```bash
# Start Redis server
redis-server
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env with your database/Redis credentials
```

Required `.env` variables:

```sh
SECRET_KEY=your-secret-key-here
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=taskflow
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/taskflow

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (Mailhog for dev)
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM=noreply@taskflow.local
```

### 4. Run database migrations

<!--TODO: use Alembic migration-->

```bash
# Tables are auto-created on startup via SQLModel
```

### 5. Start development servers

```bash
# Terminal 1: Start FastAPI server
uv run fastapi dev app/main.py

# Terminal 2: Start Celery worker
uv run celery -A app.worker worker --loglevel=info --pool=solo
```

---

## Environment Variables

| Variable        | Description                                           | Default                    |
| --------------- | ----------------------------------------------------- | -------------------------- |
| `SECRET_KEY`    | JWT secret key (generate with `openssl rand -hex 32`) | Required                   |
| `DEBUG`         | Enable debug mode                                     | `True`                     |
| `DATABASE_URL`  | PostgreSQL async connection string                    | Required                   |
| `REDIS_URL`     | Redis connection string                               | `redis://localhost:6379/0` |
| `MAIL_SERVER`   | SMTP server                                           | `localhost`                |
| `MAIL_PORT`     | SMTP port                                             | `1025`                     |
| `MAIL_USERNAME` | SMTP username                                         | ``                         |
| `MAIL_PASSWORD` | SMTP password                                         | ``                         |
| `MAIL_FROM`     | From email address                                    | `noreply@taskflow.local`   |
| `FRONTEND_URLS` | CORS allowed origins (comma-separated)                | `http://localhost:3000`    |

---

## Project Structure

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py          # Settings & config
│   │   ├── celery_app.py      # Celery app config
│   │   └── middleware.py      # Auth middleware
│   ├── db/
│   │   └── main.py            # DB engine & session
│   ├── models/                # SQLModel models
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── task.py
│   │   └── enums.py
│   ├── routes/                # API routes
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── project.py
│   │   └── task.py
│   ├── schemas/               # Pydantic schemas
│   ├── services/              # Business logic
│   └── utils/                 # Utilities (mail, etc.)
├── scripts/                   # Test scripts
├── tests/                     # (to be added)
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── uv.lock
```

<!-----
For testing use pytest
## Running Tests

```bash
# Run all test scripts
uv run python scripts/test_auth.py
uv run python scripts/test_user.py
uv run python scripts/test_project.py
uv run python scripts/test_task.py
uv run python scripts/test_project_members.py
uv run python scripts/test_admin_project.py
uv run python scripts/test_cascade.py
uv run python scripts/test_middleware.py
uv run python scripts/test_db_models.py

# Run with pytest (when tests are added)
uv run pytest
```

----->

## Development Commands

```bash
# Format code
uv run ruff format .

# Lint
uv run ruff check .

# Run with hot reload
uv run fastapi dev app/main.py

# Production mode
uv run fastapi run app/main.py

# Run Celery worker
uv run celery -A app.worker worker --loglevel=info --pool=solo

# Run Celery beat (scheduler)
uv run celery -A app.worker beat --loglevel=info
```

---

## Docker Production Build

```bash
# Build image
docker build -t taskflow-backend .

# Run container
docker run -d \
  --name taskflow-api \
  -p 8000:8000 \
  --env-file .env \
  taskflow-backend
```

<!------->

<!--## Database Migrations (Production)

When ready for production, set up Alembic:

```bash
# Initialize alembic
uv run alembic init alembic

# Configure alembic.ini and env.py for async SQLAlchemy

# Create migration
uv run alembic revision --autogenerate -m "initial"

# Apply migrations
uv run alembic upgrade head
```-->

---

## Troubleshooting

### Database connection issues

- Verify `DATABASE_URL` format: `postgresql+asyncpg://user:pass@host:port/db`
- Ensure PostgreSQL is running and accessible

### Redis connection issues

- Check `REDIS_URL` format: `redis://host:port/db`
- Verify Redis server is running

### Email not sending

- For dev: Use Mailhog (`docker-compose up mail`)
- Check `MAIL_*` environment variables

### CORS errors

- Set `FRONTEND_URLS` in `.env` (comma-separated)
- Include your frontend URL (e.g., `http://localhost:3000`)

---

## Useful Commands

```bash
# View logs
docker-compose logs -f app

# Access container shell
docker-compose exec app bash

# Run migrations in container
docker-compose exec app alembic upgrade head

# Reset database (Docker)
docker-compose down -v && docker-compose up -d
```
