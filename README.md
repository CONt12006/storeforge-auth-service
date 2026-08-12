# StoreForge Auth Service

> Authentication and authorization microservice for the **StoreForge** platform.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python\&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116-009688?logo=fastapi\&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql\&logoColor=white)](https://postgresql.org)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy\&logoColor=white)](https://sqlalchemy.org)
[![Alembic](https://img.shields.io/badge/Alembic-Migrations-orange)](https://alembic.sqlalchemy.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker\&logoColor=white)](https://docker.com)
[![JWT](https://img.shields.io/badge/Auth-JWT-success)]()

---

## Overview

**StoreForge Auth Service** — микросервис аутентификации и авторизации для платформы StoreForge.

Сервис реализует регистрацию и вход пользователей, JWT access/refresh tokens, управление пользовательскими сессиями через Redis и ролевую модель доступа.

Backend построен на **FastAPI** с асинхронной работой с PostgreSQL через **SQLAlchemy 2.0 + asyncpg**.

Архитектура разделена на API, service, repository, security и database слои.

---

## Features

* регистрация и аутентификация пользователей;
* JWT access tokens;
* refresh tokens с хранением сессий в Redis;
* refresh-token rotation;
* SHA-256 hashing refresh-токенов;
* Argon2 hashing пользовательских паролей;
* роли пользователей;
* передача ролей внутри JWT;
* защищённые endpoints через Bearer Authentication;
* асинхронная работа с PostgreSQL;
* Repository Pattern и Service Layer;
* транзакционная работа с БД;
* миграции через Alembic;
* конфигурация через environment variables;
* Docker и Docker Compose;
* OpenAPI / Swagger документация.

---

## Architecture

```text id="awtcay"
Client
  │
  ▼
FastAPI Routers
  │
  ▼
AuthService
  │
  ├───────────────┐
  ▼               ▼
Repositories    Security
  │               │
  ├── PostgreSQL  ├── JWT
  └── Redis       ├── Argon2
                  └── Refresh Tokens
```

### Layers

**API**

Обрабатывает HTTP-запросы, Pydantic validation и FastAPI dependencies.

**Service**

Содержит бизнес-логику регистрации, аутентификации, работы с токенами и пользовательскими сессиями.

**Repository**

Инкапсулирует работу с PostgreSQL и Redis.

**Security**

Отвечает за JWT, password hashing и refresh tokens.

---

## Authentication

После успешного входа клиент получает:

```text id="aitioa"
Access Token + Refresh Token
```

### Access Token

JWT access token содержит идентификатор пользователя и его роли:

```json id="r5ewr9"
{
  "sub": "42",
  "roles": ["customer"],
  "type": "access",
  "exp": 1786557600
}
```

Access token передаётся через:

```http id="mxjj5h"
Authorization: Bearer <access_token>
```

### Refresh Token

Refresh-сессии хранятся в Redis с TTL.

```text id="tdhpwh"
Refresh Token
      │
      ▼
Validate Session
      │
      ▼
Invalidate Old Token
      │
      ▼
Generate New Token Pair
```

При обновлении сессии предыдущий refresh token инвалидируется.

В Redis хранится SHA-256 hash токена, а не исходное значение.

---

## Roles

Пользователи и роли связаны отношением many-to-many:

```text id="1dxp9s"
users
  │
  ▼
user_roles
  │
  ▼
roles
```

Роли пользователя включаются в JWT и могут использоваться сервисами платформы для авторизации.

---

## API

| Method | Endpoint             | Description              |
| ------ | -------------------- | ------------------------ |
| `POST` | `/api/auth/register` | Регистрация пользователя |
| `POST` | `/api/auth/login`    | Аутентификация           |
| `POST` | `/api/auth/refresh`  | Обновление token pair    |
| `GET`  | `/api/users/me`      | Текущий пользователь     |
| `GET`  | `/health`            | Health check             |

Интерактивная документация доступна через Swagger:

```text id="1y607d"
http://localhost:8000/docs
```

---

## Tech Stack

| Technology     | Purpose             |
| -------------- | ------------------- |
| Python 3.12    | Backend             |
| FastAPI        | REST API            |
| Pydantic       | Data validation     |
| SQLAlchemy 2.0 | Async ORM           |
| asyncpg        | PostgreSQL driver   |
| PostgreSQL 16  | Persistent storage  |
| Redis          | Refresh sessions    |
| Alembic        | Database migrations |
| Argon2         | Password hashing    |
| python-jose    | JWT                 |
| Uvicorn        | ASGI server         |
| Docker         | Containerization    |
| Ruff           | Linting             |
| pytest         | Testing             |

---

## Project Structure

```text id="o4fpel"
src/auth_service/
├── api/
│   ├── auth.py
│   ├── dependencies.py
│   └── users.py
├── database/
│   ├── database.py
│   ├── models.py
│   └── redis.py
├── repositories/
│   ├── refresh_token_repository.py
│   ├── role_repository.py
│   └── user_repository.py
├── schemas/
├── security/
│   ├── jwt.py
│   ├── password.py
│   └── refresh_token.py
├── services/
│   └── auth_service.py
├── config.py
└── main.py
```

---

## Running Locally

### Docker Compose

```bash id="b9ygli"
docker compose up --build
```

### Local environment

```bash id="qb8g2a"
python -m venv .venv
source .venv/bin/activate

python -m pip install -e ".[dev]"
python -m alembic upgrade head

uvicorn auth_service.main:app --reload --app-dir src
```

После запуска:

```text id="bd9k5n"
API:     http://localhost:8000
Swagger: http://localhost:8000/docs
```

---

## Database

Основные таблицы:

```text id="l9dn8i"
users
roles
user_roles
```

Регистрация пользователя и назначение роли выполняются транзакционно.

Схема PostgreSQL версионируется через **Alembic migrations**.

---

## Security

В сервисе используются:

* Argon2 для хеширования паролей;
* JWT для access tokens;
* server-side refresh sessions в Redis;
* refresh-token rotation;
* SHA-256 hashing refresh tokens;
* TTL для автоматического завершения refresh-сессий;
* Bearer Authentication для защищённых endpoints;
* environment variables для конфигурации секретов.
