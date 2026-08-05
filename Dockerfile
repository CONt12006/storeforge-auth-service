# syntax=docker/dockerfile:1.6

FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install uv

COPY pyproject.toml requirements.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install \
    --system \
    -r requirements.lock


FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

COPY --from=builder \
    /usr/local/lib/python3.12/site-packages \
    /usr/local/lib/python3.12/site-packages

COPY --from=builder \
    /usr/local/bin \
    /usr/local/bin

COPY src /app/src
COPY alembic /app/alembic
COPY alembic.ini /app/alembic.ini

RUN useradd \
    --system \
    --uid 10001 \
    --create-home \
    app

USER app

EXPOSE 8000

CMD ["uvicorn", "auth_service.main:app", "--host", "0.0.0.0", "--port", "8000"]