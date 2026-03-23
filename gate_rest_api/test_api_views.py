import os
import importlib
import pytest

from httpx import ASGITransport, AsyncClient

os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")

from app import app

# Такой вариант устойчивее и не зависит от того, как устроен views/__init__.py.
spot_view = importlib.import_module("views.spot")
wallet_view = importlib.import_module("views.wallet")


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


@pytest.fixture
async def api_client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.mark.anyio
async def test_spot_orders_success(monkeypatch, api_client):
    class FakeSpot:
        async def list_orders(self, currency_pair, status):
            assert currency_pair == "BTC_USDT"
            assert status == "open"
            return [{"id": "1", "status": "open"}]

    def fake_create_instance(*args, **kwargs):
        return FakeSpot()

    monkeypatch.setattr(spot_view, "create_instanse", fake_create_instance)
    response = await api_client.post(
        "/spot/orders?currency_pair=BTC_USDT&status=open",
        json={"key": "k", "proxy": None, "secret": "s"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data[0]["id"] == "1"


@pytest.mark.anyio
async def test_spot_orders_invalid_status_422(api_client):
    response = await api_client.post(
        "/spot/orders?currency_pair=BTC_USDT&status=bad",
        json={"key": "kkkkkk", "proxy": None, "secret": "ssssss"},
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_wallet_total_balance_success(monkeypatch, api_client):
    class FakeWallet:
        async def total_balance(self):
            return {
                "details": {
                    "spot": {"currency": "USDT", "amount": "100"},
                    "cross_margin": {},
                    "finance": {},
                    "margin": {},
                    "quant": {},
                    "futures": {},
                    "delivery": {},
                    "warrant": {},
                    "cbbc": {},
                },
                "total": {"currency": "USDT", "amount": "100"},
            }

    def fake_create_instance(*args, **kwargs):
        return FakeWallet()

    monkeypatch.setattr(wallet_view, "create_instanse", fake_create_instance)
    response = await api_client.post(
        "/wallet/total_balance",
        json={"key": "kkkkkkk", "proxy": None, "secret": "ssssss"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"]["currency"] == "USDT"
    assert data["details"]["spot"]["amount"] == "100"
