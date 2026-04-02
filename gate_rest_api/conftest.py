import os
import pytest

from httpx import ASGITransport, AsyncClient

os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")

from app import app

@pytest.fixture(autouse=True)
async def initialize_limiter():
    
    import redis.asyncio as redis
    from fastapi_limiter import FastAPILimiter
    redis_instance = redis.from_url("redis://localhost:6379", encoding="utf8")
    await FastAPILimiter.init(redis_instance)
    yield
    await FastAPILimiter.close()

@pytest.fixture(autouse=True)
def disable_startup_events():
    """Отключаем все события startup"""
    original_startup = list(app.router.on_startup)
    app.router.on_startup.clear()
    try:
        yield
    finally:
        app.router.on_startup[:] = original_startup


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="function")
async def api_client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client