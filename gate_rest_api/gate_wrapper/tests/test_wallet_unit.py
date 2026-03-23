import pytest

from gate_wrapper.model import TotalBalance
from gate_wrapper.wallet import Wallet


class DummyObject:
    def __init__(self, payload):
        self._payload = payload

    def to_dict(self):
        return self._payload


class DummyAsyncResult:
    def __init__(self, value):
        self._value = value

    def get(self):
        return self._value


def _wrap_response(payload, async_req):
    if async_req:
        return DummyAsyncResult(payload)
    return payload


class FakeWalletApi:
    def get_total_balance(self, *args, **kwargs):
        payload = DummyObject(
            {
                "details": {
                    "cross_margin": {},
                    "spot": {"currency": "USDT", "amount": "100.0"},
                    "finance": {},
                    "margin": {},
                    "quant": {},
                    "futures": {},
                    "delivery": {},
                    "warrant": {},
                    "cbbc": {},
                },
                "total": {"currency": "USDT", "amount": "100.0"},
            }
        )
        return _wrap_response(payload, kwargs.get("async_req", False))


@pytest.fixture
def wallet_instance():
    return Wallet(api_client=None, instance=FakeWalletApi())


@pytest.mark.asyncio
@pytest.mark.parametrize("async_req", [False, True])
async def test_total_balance(async_req, wallet_instance):
    result = await wallet_instance.total_balance(async_req=async_req)
    assert isinstance(result, TotalBalance)
    assert result.total.currency == "USDT"
    assert result.details.spot.amount == "100.0"
