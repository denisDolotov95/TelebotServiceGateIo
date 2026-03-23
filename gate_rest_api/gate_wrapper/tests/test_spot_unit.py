import pytest

from gate_wrapper.model import CurrencyPair, Order, Ticker
from gate_wrapper.spot import Spot


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


@pytest.mark.asyncio
async def test_list_tickers_sync_parses_models():
    class FakeSpotApi:
        def list_tickers(self, *args, **kwargs):
            return [DummyObject({"currency_pair": "BTC_USDT", "last": "50000"})]

    spot = Spot(api_client=None, instance=FakeSpotApi())
    result = await spot.list_tickers(currency_pair="BTC_USDT")

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], Ticker)
    assert result[0].currency_pair == "BTC_USDT"


@pytest.mark.asyncio
async def test_cancel_orders_async_req_uses_get():
    class FakeSpotApi:
        def cancel_orders(self, *args, **kwargs):
            assert kwargs["currency_pair"] == "BTC_USDT"
            assert kwargs["async_req"] is True
            return DummyAsyncResult([DummyObject({"id": "1", "status": "cancelled"})])

    spot = Spot(api_client=None, instance=FakeSpotApi())
    result = await spot.cancel_orders(currency_pair="BTC_USDT", async_req=True)

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], Order)
    assert result[0].status == "cancelled"


@pytest.mark.asyncio
async def test_list_currency_pairs_async_req_parses_currency_pair():
    class FakeSpotApi:
        def list_currency_pairs(self, *args, **kwargs):
            assert kwargs["async_req"] is True
            return DummyAsyncResult([DummyObject({"id": "BTC_USDT"})])

    spot = Spot(api_client=None, instance=FakeSpotApi())
    result = await spot.list_currency_pairs(async_req=True)

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], CurrencyPair)
    assert result[0].id == "BTC_USDT"
