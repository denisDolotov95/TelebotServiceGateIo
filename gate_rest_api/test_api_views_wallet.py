import importlib
import pytest

# Такой вариант устойчивее и не зависит от того, как устроен views/__init__.py.
wallet_view = importlib.import_module("views.wallet")

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


def fake_wallet_create_instance(*args, **kwargs):
    return FakeWallet()


@pytest.mark.anyio
async def test_wallet_total_balance_success(monkeypatch, api_client):

    monkeypatch.setattr(wallet_view, "create_instanse", fake_wallet_create_instance)
    response = await api_client.post(
        "/wallet/total_balance",
        json={"key": "kkkkkkk", "proxy": None, "secret": "ssssss"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"]["currency"] == "USDT"
    assert data["details"]["spot"]["amount"] == "100"
