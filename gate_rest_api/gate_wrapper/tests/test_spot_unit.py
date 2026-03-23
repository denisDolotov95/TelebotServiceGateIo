import pytest

from gate_wrapper.model import (
    Account,
    AccountBook,
    Candlestick,
    CurrencyPair,
    OpenOrders,
    Order,
    OrderBook,
    Ticker,
    Trade,
)
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


def _wrap_response(payload, async_req):
    if async_req:
        return DummyAsyncResult(payload)
    return payload


class FakeSpotApi:
    def get_currency_pair(self, *args, **kwargs):
        return _wrap_response(
            DummyObject({"id": kwargs["currency_pair"], "base": "BTC", "quote": "USDT"}),
            kwargs.get("async_req", False),
        )

    def cancel_orders(self, *args, **kwargs):
        return _wrap_response(
            [DummyObject({"id": "1", "status": "cancelled"})],
            kwargs.get("async_req", False),
        )

    def list_orders(self, *args, **kwargs):
        return _wrap_response(
            [DummyObject({"id": "1", "status": kwargs["status"]})],
            kwargs.get("async_req", False),
        )

    def list_tickers(self, *args, **kwargs):
        return _wrap_response(
            [DummyObject({"currency_pair": "BTC_USDT", "last": "50000"})],
            kwargs.get("async_req", False),
        )

    def list_currency_pairs(self, *args, **kwargs):
        return _wrap_response(
            [DummyObject({"id": "BTC_USDT"})],
            kwargs.get("async_req", False),
        )

    def list_spot_accounts(self, *args, **kwargs):
        return _wrap_response(
            [DummyObject({"currency": "USDT", "available": "10"})],
            kwargs.get("async_req", False),
        )

    def list_spot_account_book(self, *args, **kwargs):
        return _wrap_response(
            [DummyObject({"id": "1", "currency": "USDT", "change": "1.0"})],
            kwargs.get("async_req", False),
        )

    def list_trades(self, *args, **kwargs):
        return _wrap_response(
            [DummyObject({"id": 1, "price": "50000", "amount": "0.1"})],
            kwargs.get("async_req", False),
        )

    def list_order_book(self, *args, **kwargs):
        return _wrap_response(
            DummyObject(
                {
                    "id": 1,
                    "current": 100,
                    "update": 101,
                    "asks": [["50000", "1.0"]],
                    "bids": [["49900", "2.0"]],
                }
            ),
            kwargs.get("async_req", False),
        )

    def list_all_open_orders(self, *args, **kwargs):
        return _wrap_response(
            [
                DummyObject(
                    {
                        "currency_pair": "BTC_USDT",
                        "total": 1,
                        "orders": [{"id": "1", "status": "open"}],
                    }
                )
            ],
            kwargs.get("async_req", False),
        )

    def list_candlesticks(self, *args, **kwargs):
        return _wrap_response(
            [["1630000000", 10.0, "50000", "51000", "49000", "49500", 0.5, True]],
            kwargs.get("async_req", False),
        )


@pytest.fixture(scope="module")
def spot_instance():
    return Spot(api_client=None, instance=FakeSpotApi())


@pytest.mark.asyncio
@pytest.mark.parametrize("async_req", [False, True])
async def test_currency_pair(async_req, spot_instance):
    result = await spot_instance.currency_pair(currency_pair="BTC_USDT", async_req=async_req)
    assert isinstance(result, CurrencyPair)
    assert result.id == "BTC_USDT"


@pytest.mark.asyncio
@pytest.mark.parametrize("async_req", [False, True])
async def test_cancel_orders(async_req, spot_instance):
    result = await spot_instance.cancel_orders(currency_pair="BTC_USDT", async_req=async_req)
    assert isinstance(result, list)
    assert isinstance(result[0], Order)
    assert result[0].status == "cancelled"


@pytest.mark.asyncio
@pytest.mark.parametrize("async_req", [False, True])
async def test_list_orders(async_req, spot_instance):
    result = await spot_instance.list_orders(
        currency_pair="BTC_USDT", status="open", async_req=async_req
    )
    assert isinstance(result, list)
    assert isinstance(result[0], Order)
    assert result[0].status == "open"


@pytest.mark.asyncio
@pytest.mark.parametrize("async_req", [False, True])
async def test_list_tickers(async_req, spot_instance):
    result = await spot_instance.list_tickers(currency_pair="BTC_USDT", async_req=async_req)
    assert isinstance(result, list)
    assert isinstance(result[0], Ticker)
    assert result[0].currency_pair == "BTC_USDT"


@pytest.mark.asyncio
@pytest.mark.parametrize("async_req", [False, True])
async def test_list_currency_pairs(async_req, spot_instance):
    result = await spot_instance.list_currency_pairs(async_req=async_req)
    assert isinstance(result, list)
    assert isinstance(result[0], CurrencyPair)
    assert result[0].id == "BTC_USDT"


@pytest.mark.asyncio
@pytest.mark.parametrize("async_req", [False, True])
async def test_list_spot_accounts(async_req, spot_instance):
    result = await spot_instance.list_spot_accounts(async_req=async_req)
    assert isinstance(result, list)
    assert isinstance(result[0], Account)
    assert result[0].currency == "USDT"


@pytest.mark.asyncio
@pytest.mark.parametrize("async_req", [False, True])
async def test_list_spot_account_book(async_req, spot_instance):
    result = await spot_instance.list_spot_account_book(async_req=async_req)
    assert isinstance(result, list)
    assert isinstance(result[0], AccountBook)
    assert result[0].id == "1"


@pytest.mark.asyncio
@pytest.mark.parametrize("async_req", [False, True])
async def test_list_trades(async_req, spot_instance):
    result = await spot_instance.list_trades(currency_pair="BTC_USDT", async_req=async_req)
    assert isinstance(result, list)
    assert isinstance(result[0], Trade)
    assert result[0].id == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("async_req", [False, True])
async def test_order_book(async_req, spot_instance):
    result = await spot_instance.order_book(currency_pair="BTC_USDT", async_req=async_req)
    assert isinstance(result, OrderBook)
    assert result.id == 1
    assert len(result.asks) == 1
    assert len(result.bids) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("async_req", [False, True])
async def test_list_all_open_orders(async_req, spot_instance):
    result = await spot_instance.list_all_open_orders(async_req=async_req)
    assert isinstance(result, list)
    assert isinstance(result[0], OpenOrders)
    assert result[0].currency_pair == "BTC_USDT"
    assert len(result[0].orders) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("async_req", [False, True])
async def test_list_candlesticks(async_req, spot_instance):
    result = await spot_instance.list_candlesticks(
        currency_pair="BTC_USDT", async_req=async_req
    )
    assert isinstance(result, list)
    assert isinstance(result[0], Candlestick)
    assert result[0].unix_timestamp == "1630000000"
