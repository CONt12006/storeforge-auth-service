from fastapi import FastAPI

from src.auth_service.api.auth import router as auth_router


app = FastAPI(title="StoreForge Auth Service")

app.include_router(
    auth_router,
    prefix="/api/auth",
    tags=["auth"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Проверяет, что приложение запущено."""

    return {"status": "ok"}