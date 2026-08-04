# storeforge-auth-service
StoreForge Auth Service — микросервис аутентификации и управления пользователями платформы StoreForge. Отвечает за регистрацию пользователей, авторизацию, управление JWT access/refresh токенами, ролями, профилями пользователей и публикацию событий для других микросервисов через RabbitMQ.


## Что должен уметь Auth Service

### 1. Регистрация пользователя

Endpoint:

```http
POST /api/v1/auth/register
```

Принимает:

```json
{
  "email": "user@example.com",
  "password": "StrongPassword123",
  "first_name": "Alex",
  "last_name": "Black"
}
```

Что происходит внутри:

1. Проверяешь, что email ещё не занят.
2. Проверяешь требования к паролю.
3. Хешируешь пароль.
4. Создаёшь пользователя в PostgreSQL.
5. Назначаешь стандартную роль `customer`.
6. Публикуешь событие `user.registered` в RabbitMQ.
7. Возвращаешь созданного пользователя без пароля.

Пример ответа:

```json
{
  "id": "7af2f799-3267-4ba5-a5b0-241eb8143e70",
  "email": "user@example.com",
  "first_name": "Alex",
  "last_name": "Black",
  "role": "customer",
  "is_active": true
}
```

---

### 2. Вход в систему

Endpoint:

```http
POST /api/v1/auth/login
```

Принимает:

```json
{
  "email": "user@example.com",
  "password": "StrongPassword123"
}
```

Логика:

1. Находишь пользователя по email.
2. Берёшь хеш пароля из PostgreSQL.
3. Сравниваешь введённый пароль с хешем.
4. Проверяешь, что пользователь активен.
5. Создаёшь `access token`.
6. Создаёшь `refresh token`.
7. Сохраняешь информацию о refresh token.
8. Возвращаешь токены клиенту.

Ответ:

```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "expires_in": 900
}
```

## Access token

Это короткоживущий JWT, например на 15 минут.

Внутри него могут быть поля:

```json
{
  "sub": "7af2f799-3267-4ba5-a5b0-241eb8143e70",
  "email": "user@example.com",
  "roles": ["customer"],
  "type": "access",
  "iat": 1785866400,
  "exp": 1785867300,
  "jti": "30d3051d-58e2-4aa6-99f6-b2443369938f"
}
```

Где:

* `sub` — ID пользователя;
* `roles` — роли;
* `exp` — время окончания действия;
* `jti` — уникальный идентификатор токена;
* `type` — тип токена.

Именно этот токен клиент отправляет другим сервисам:

```http
Authorization: Bearer eyJhbGciOi...
```

Например, `Order Service` проверяет JWT и понимает, какой пользователь создаёт заказ.

## Refresh token

Refresh token живёт дольше, например 7–30 дней.

Он нужен, чтобы получить новый access token без повторного ввода пароля.

Endpoint:

```http
POST /api/v1/auth/refresh
```

Запрос:

```json
{
  "refresh_token": "eyJhbGciOi..."
}
```

Ответ:

```json
{
  "access_token": "new-access-token",
  "refresh_token": "new-refresh-token",
  "token_type": "bearer",
  "expires_in": 900
}
```

Лучше реализовать **refresh token rotation**:

1. Клиент отправляет refresh token.
2. Старый refresh token отзывается.
3. Создаётся новая пара токенов.
4. Повторно использовать старый refresh token нельзя.

Это защищает от кражи токена.

---

## 3. Выход из системы

Endpoint:

```http
POST /api/v1/auth/logout
```

При выходе ты отзываешь refresh token.

Например:

```json
{
  "refresh_token": "eyJhbGciOi..."
}
```

После этого обновить access token через этот refresh token нельзя.

Сам access token обычно не удаляется моментально, а просто доживает свои 10–15 минут. Поэтому access token должен иметь короткий срок жизни.

---

## 4. Получение текущего пользователя

Endpoint:

```http
GET /api/v1/users/me
```

Заголовок:

```http
Authorization: Bearer <access-token>
```

Ответ:

```json
{
  "id": "7af2f799-3267-4ba5-a5b0-241eb8143e70",
  "email": "user@example.com",
  "first_name": "Alex",
  "last_name": "Black",
  "roles": ["customer"],
  "is_active": true
}
```

Этот endpoint проверяет JWT, извлекает `sub` и загружает пользователя из БД.

---

## 5. Управление профилем

Можно добавить:

```http
PATCH /api/v1/users/me
```

Например:

```json
{
  "first_name": "Alexander",
  "last_name": "Black"
}
```

И отдельно смену пароля:

```http
POST /api/v1/users/me/change-password
```

```json
{
  "current_password": "OldPassword123",
  "new_password": "NewPassword456"
}
```

Перед сменой обязательно проверяешь текущий пароль.

---

## 6. Роли и права

На первом этапе хватит ролей:

```text
customer
admin
```

Позже можно добавить:

```text
seller
support
manager
```

Пример правил:

| Роль       | Возможности                                                |
| ---------- | ---------------------------------------------------------- |
| `customer` | смотреть товары, управлять корзиной, создавать свои заказы |
| `seller`   | управлять своими товарами                                  |
| `admin`    | управлять пользователями, товарами и заказами              |

В JWT можно хранить:

```json
{
  "roles": ["customer"]
}
```

Но важно понимать: JWT содержит снимок ролей на момент выдачи токена. Если администратор изменил роль пользователя, старый access token может действовать ещё несколько минут. Поэтому access token должен быть короткоживущим.

---

## 7. Административное управление пользователями

Для администратора:

```http
GET /api/v1/admin/users
GET /api/v1/admin/users/{user_id}
PATCH /api/v1/admin/users/{user_id}/roles
POST /api/v1/admin/users/{user_id}/block
POST /api/v1/admin/users/{user_id}/unblock
```

Например, назначение роли:

```json
{
  "roles": ["customer", "seller"]
}
```

Обычный пользователь не должен иметь доступ к этим endpoint.

---

# Что хранить в PostgreSQL

## Таблица `users`

Пример:

```text
users
-----
id
email
password_hash
first_name
last_name
is_active
is_verified
created_at
updated_at
last_login_at
```

Приблизительная SQLAlchemy-модель:

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    first_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    last_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
```

## Таблица `roles`

```text
roles
-----
id
name
description
```

## Таблица связи `user_roles`

```text
user_roles
----------
user_id
role_id
```

Это позволяет одному пользователю иметь несколько ролей.

## Таблица `refresh_tokens`

Не стоит хранить refresh token в открытом виде. Храни его хеш.

```text
refresh_tokens
--------------
id
user_id
token_hash
jti
expires_at
revoked_at
created_at
device_info
ip_address
```

При обновлении токена:

1. Получаешь refresh token.
2. Вычисляешь его хеш.
3. Ищешь хеш в БД.
4. Проверяешь, что токен не отозван.
5. Проверяешь срок действия.
6. Отзываешь его и создаёшь новый.

---

# Что хранить в Vault или OpenBao

В Vault/OpenBao нужно хранить **секреты приложения**, а не пароли пользователей.

Там должны находиться:

```text
JWT_PRIVATE_KEY
JWT_PUBLIC_KEY
DATABASE_PASSWORD
RABBITMQ_PASSWORD
REDIS_PASSWORD
EMAIL_PROVIDER_API_KEY
```

Не нужно хранить в Vault каждый пользовательский пароль.

Правильная схема такая:

```text
Пароль пользователя
        ↓
Argon2id
        ↓
password_hash
        ↓
PostgreSQL
```

То есть в PostgreSQL лежит только необратимый хеш:

```text
$argon2id$v=19$m=65536,t=3,p=4$...
```

Из него нельзя получить исходный пароль. При авторизации ты не расшифровываешь пароль, а проверяешь:

```python
password_hasher.verify(
    stored_hash,
    entered_password,
)
```

Для хеширования лучше использовать `Argon2id`.

---

# JWT: симметричная или асимметричная подпись

Для микросервисной архитектуры лучше использовать асимметричный вариант:

```text
Auth Service:
JWT_PRIVATE_KEY

Остальные сервисы:
JWT_PUBLIC_KEY
```

Auth Service подписывает токены приватным ключом:

```text
RS256 или EdDSA
```

Остальные сервисы проверяют подпись публичным ключом.

Преимущество: `Order Service`, `Cart Service` и `Product Service` могут проверять JWT, но не могут выпускать собственные токены.

Схема:

```text
Пользователь
    |
    | POST /login
    v
Auth Service
    |
    | подписывает JWT private key
    v
Access token
    |
    +-----------> Order Service
    |
    +-----------> Cart Service
    |
    +-----------> Product Service

Все сервисы проверяют токен public key.
```

---

# События RabbitMQ

Auth Service может публиковать:

```text
user.registered
user.updated
user.blocked
user.unblocked
user.role_changed
user.deleted
```

Пример `user.registered`:

```json
{
  "event_id": "94914409-8b21-4c4f-b5fd-b1cb6a697f23",
  "event_type": "user.registered",
  "occurred_at": "2026-08-04T15:30:00Z",
  "data": {
    "user_id": "7af2f799-3267-4ba5-a5b0-241eb8143e70",
    "email": "user@example.com",
    "first_name": "Alex",
    "last_name": "Black"
  }
}
```

Например, `Notification Service` получает это событие и отправляет приветственное письмо.

Но пароль, хеш пароля, access token и refresh token в RabbitMQ публиковать нельзя.

---

# Рекомендуемая структура проекта

```text
storeforge-auth-service/
├── src/
│   └── auth_service/
│       ├── main.py
│       ├── config.py
│       │
│       ├── api/
│       │   ├── dependencies.py
│       │   └── v1/
│       │       ├── auth.py
│       │       ├── users.py
│       │       └── admin.py
│       │
│       ├── models/
│       │   ├── user.py
│       │   ├── role.py
│       │   └── refresh_token.py
│       │
│       ├── schemas/
│       │   ├── auth.py
│       │   ├── user.py
│       │   └── token.py
│       │
│       ├── repositories/
│       │   ├── user_repository.py
│       │   ├── role_repository.py
│       │   └── token_repository.py
│       │
│       ├── services/
│       │   ├── auth_service.py
│       │   ├── user_service.py
│       │   └── token_service.py
│       │
│       ├── security/
│       │   ├── password.py
│       │   ├── jwt.py
│       │   └── permissions.py
│       │
│       ├── database/
│       │   ├── base.py
│       │   ├── session.py
│       │   └── migrations/
│       │
│       ├── messaging/
│       │   ├── publisher.py
│       │   └── events.py
│       │
│       └── exceptions/
│           └── auth.py
│
├── tests/
│   ├── unit/
│   └── integration/
├── alembic/
├── alembic.ini
├── pyproject.toml
├── Dockerfile
└── README.md
```

Разделение ответственности:

```text
api          — принимает HTTP-запросы
schemas      — проверяет входные и выходные данные
services     — бизнес-логика
repositories — запросы к PostgreSQL
models       — таблицы SQLAlchemy
security     — пароли, JWT и авторизация
messaging    — публикация событий RabbitMQ
```

Например, endpoint не должен сам хешировать пароль и писать SQL:

```python
@router.post("/register")
async def register(
    request: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    return await service.register(request)
```

А основная логика находится в сервисе:

```python
class AuthService:
    async def register(self, request: RegisterRequest) -> User:
        existing_user = await self.user_repository.get_by_email(
            request.email
        )

        if existing_user is not None:
            raise EmailAlreadyExistsError()

        password_hash = self.password_hasher.hash(
            request.password
        )

        user = await self.user_repository.create(
            email=request.email,
            password_hash=password_hash,
            first_name=request.first_name,
            last_name=request.last_name,
        )

        await self.event_publisher.publish_user_registered(user)

        return user
```

# Минимальная первая версия

Для первого рабочего MVP тебе достаточно реализовать:

1. PostgreSQL и миграции Alembic.
2. Таблицу `users`.
3. Таблицы `roles` и `user_roles`.
4. Таблицу `refresh_tokens`.
5. Регистрацию.
6. Вход.
7. Выдачу access и refresh token.
8. Обновление токенов.
9. Logout.
10. `GET /users/me`.
11. Хеширование через Argon2id.
12. JWT с приватным и публичным ключом.
13. Роли `customer` и `admin`.
14. Публикацию `user.registered`.
15. Unit- и integration-тесты.

А восстановление пароля, подтверждение email, OAuth через Google и двухфакторную аутентификацию лучше добавлять после базового рабочего варианта.
