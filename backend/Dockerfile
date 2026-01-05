
FROM python:3.12-slim AS base
# get base image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
# setup working dir

ENV UV_COMPILE_BYTECODE=1
# for faster byte code compiletion

ENV UV_LINK_MODE=copy

# install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=uv.lock,target=uv.lock \
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  uv sync --locked --no-install-project

# copy source
COPY . /app

# install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --locked

# FROM base

RUN useradd -m -u 405 appuser
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["/app/.venv/bin/fastapi", "run", "app/main.py", "--port", "8000", "--host", "0.0.0.0"]
