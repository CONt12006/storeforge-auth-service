# StoreForge Auth Service

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)](https://postgresql.org)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white)](https://sqlalchemy.org)
[![Alembic](https://img.shields.io/badge/Alembic-Migrations-orange)](https://alembic.sqlalchemy.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![JWT](https://img.shields.io/badge/Auth-JWT-success)]()

------------------------------------------------------------------------

## О проекте

**StoreForge Auth Service** --- отдельный микросервис платформы
StoreForge, отвечающий за регистрацию пользователей, аутентификацию,
авторизацию и управление ролями.

На текущий момент реализованы:

-   регистрация пользователя;
-   вход по email и паролю;
-   безопасное хеширование паролей (Argon2);
-   выдача JWT access token;
-   получение текущего пользователя по JWT;
-   роли пользователей (`customer`);
-   миграции Alembic;
-   Docker и Docker Compose.

------------------------------------------------------------------------

# Архитектура

``` text
HTTP Request
      │
      ▼
 FastAPI Router
      │
      ▼
 AuthService
      │
      ▼
 Repository
      │
      ▼
 PostgreSQL
```

### Router

Принимает HTTP-запросы, валидирует входные данные через Pydantic и
вызывает сервисный слой.

### Service

Содержит бизнес-логику:

-   регистрация;
-   авторизация;
-   проверка JWT;
-   назначение ролей.

### Repository

Работает исключительно с базой данных.

### Database

PostgreSQL + SQLAlchemy ORM.

------------------------------------------------------------------------

## Используемые технологии

| Технология | Назначение |
|------------|------------|
| Python 3.12 | Основной язык разработки |
| FastAPI | Создание REST API |
| SQLAlchemy 2 | ORM и взаимодействие с PostgreSQL |
| PostgreSQL | Хранение пользователей, ролей и данных аутентификации |
| Alembic | Управление миграциями базы данных |
| Pydantic | Валидация входных и выходных данных |
| Pydantic Settings | Загрузка конфигурации из `.env` |
| python-jose | Создание и проверка JWT-токенов |
| pwdlib (Argon2) | Безопасное хеширование и проверка паролей |
| Uvicorn | ASGI-сервер для запуска FastAPI |
| Docker | Контейнеризация приложения |
| Docker Compose | Локальный запуск микросервиса и PostgreSQL |

------------------------------------------------------------------------

# Структура проекта

``` text
storeforge-auth-service/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.lock
├── alembic.ini
├── alembic/
└── src/
    └── auth_service/
        ├── api/
        ├── config.py
        ├── database/
        ├── repositories/
        ├── schemas/
        ├── security/
        ├── services/
        └── main.py
```

------------------------------------------------------------------------

# REST API

  Метод   Endpoint                Описание
  ------- ----------------------- ----------------------
  POST    /api/v1/auth/register   Регистрация
  POST    /api/v1/auth/login      Вход
  GET     /api/v1/users/me        Текущий пользователь
  GET     /health                 Проверка сервиса

## Пример регистрации

``` http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email":"alex@example.com",
  "password":"StrongPassword123",
  "first_name":"Alex",
  "last_name":"Black"
}
```

Ответ:

``` json
{
  "id":1,
  "email":"alex@example.com",
  "first_name":"Alex",
  "last_name":"Black",
  "is_active":true
}
```

------------------------------------------------------------------------

# JWT

    email + password
            │
            ▼
    проверка пользователя
            │
            ▼
    проверка Argon2
            │
            ▼
    создание JWT
            │
            ▼
    Bearer eyJhbGciOi...

Для доступа к защищённым endpoint:

    Authorization: Bearer <JWT_TOKEN>

------------------------------------------------------------------------

# База данных

``` text
users
 │
 ├──────────────┐
 │              │
 ▼              ▼
user_roles    roles
```

Основные таблицы:

-   users
-   roles
-   user_roles
-   alembic_version

------------------------------------------------------------------------

# Docker

Локальный запуск:

``` bash
docker compose up --build
```

Поднимаются контейнеры:

``` text
PostgreSQL
     │
     ▼
Alembic Migration
     │
     ▼
Auth Service
```

Swagger:

    http://127.0.0.1:8000/docs

------------------------------------------------------------------------

# Локальный запуск без Docker

``` bash
python -m venv .venv
source .venv/bin/activate

python -m pip install -e ".[dev]"

python -m alembic upgrade head

uvicorn auth_service.main:app --reload --app-dir src
```

------------------------------------------------------------------------

# Roadmap

-   ✅ Регистрация
-   ✅ Авторизация
-   ✅ JWT
-   ✅ Роли
-   ✅ Alembic
-   ✅ Docker
-   ⬜ Refresh Token
-   ⬜ Redis
-   ⬜ RabbitMQ
-   ⬜ Email Verification
-   ⬜ Password Reset
-   ⬜ OpenTelemetry
-   ⬜ CI/CD

------------------------------------------------------------------------

# Автор

Проект разработан как pet-проект в рамках платформы **StoreForge** для
изучения:

-   FastAPI;
-   микросервисной архитектуры;
-   PostgreSQL;
-   SQLAlchemy 2;
-   Alembic;
-   JWT-аутентификации;
-   Docker;
-   Docker Compose;
-   REST API.
