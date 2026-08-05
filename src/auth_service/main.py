from fastapi import FastAPI

from auth_service.api.auth import router as auth_router
from auth_service.api.users import router as users_router


app = FastAPI(title="StoreForge Auth Service")

app.include_router(
    auth_router,
    prefix="/api/auth",
    tags=["auth"],
)

app.include_router(
    users_router,
    prefix="/api/users",
    tags=["users"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Проверяет, что приложение запущено."""

    return {"status": "ok"}