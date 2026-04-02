import importlib
import pytest

# Такой вариант устойчивее и не зависит от того, как устроен views/__init__.py.
spot_view = importlib.import_module("views.spot")


class FakeSpot:

    async def list_orders(self, currency_pair: str, status: str) -> list[dict]:

        assert currency_pair == "BTC_USDT"
        assert status == "open"
        return [{"id": "1", "status": "open"}]

    async def cancel_orders(self, currency_pair: str) -> list[dict]:

        assert currency_pair == "BTC_USDT"
        return [
            {
                "id": "12332324",
                "amend_text": "t-123456",
                "text": "t-123456",
                "succeeded": True,
                "label": "",
                "message": "",
                "id": "12332324",
                "create_time": "1548000000",
                "update_time": "1548000100",
                "create_time_ms": 1548000000123,
                "update_time_ms": 1548000100123,
                "currency_pair": "ETC_BTC",
                "status": "cancelled",
                "type": "limit",
                "account": "spot",
                "side": "buy",
                "amount": "1",
                "price": "5.00032",
                "time_in_force": "gtc",
                "iceberg": "0",
                "left": "0.5",
                "filled_amount": "1.242",
                "filled_total": "2.50016",
                "avg_deal_price": "5.00032",
                "fee": "0.005",
                "fee_currency": "ETH",
                "point_fee": "0",
                "gt_fee": "0",
                "gt_discount": False,
                "rebated_fee": "0",
                "rebated_fee_currency": "BTC",
                "stp_act": "cn",
                "finish_as": "stp",
                "stp_id": 10240,
            }
        ]

    async def currency_pair(self, currency_pair: str) -> dict:

        assert currency_pair == "BTC_USDT"
        return {
            "id": currency_pair,
            "base": "BTC",
            "quote": "USDT",
            "fee": "0.2",
            "min_base_amount": "0.000001",
            "min_quote_amount": "3",
            "max_base_amount": "100",
            "max_quote_amount": "5000000",
            "amount_precision": 6,
            "precision": 1,
            "trade_status": "tradable",
            "sell_start": 0,
            "buy_start": 0,
        }

    async def list_candlesticks(
        self,
        currency_pair: str,
        limit: int = 1,
        _request_timeout: tuple[int, int] = (5, 30),
        interval: str = "10s",
    ) -> list[dict]:

        assert currency_pair == "BTC_USDT"
        assert isinstance(limit, int) and limit == 1
        assert (
            isinstance(_request_timeout, tuple)
            and _request_timeout[0] == 5
            and _request_timeout[1] == 30
        )
        assert interval in (
            "10s",
            "1m",
            "5m",
            "15m",
            "30m",
            "1h",
            "4h",
            "8h",
            "1d",
            "7d",
            "30d",
            None,
        )
        return [
            {
                "unix_timestamp": "1775129480",
                "trade_volume_in_quote": 67444.1576742,
                "close_price": "66468.1",
                "highest_price": "66472",
                "lowest_price": "66468.1",
                "open_price": "66472",
                "trade_volume_in_base": 1.014651,
                "window_is_closed": False,
            }
        ]


def fake_spot_create_instance(*args, **kwargs):
    return FakeSpot()


@pytest.mark.anyio
async def test_spot_orders_success(monkeypatch, api_client):

    monkeypatch.setattr(spot_view, "create_instanse", fake_spot_create_instance)
    response = await api_client.post(
        "/spot/orders?currency_pair=BTC_USDT&status=open",
        json={"key": "k", "proxy": None, "secret": "s"},
    )

    assert response.status_code == 200
    response_data = response.json()
    test_data = await FakeSpot().list_orders("BTC_USDT", "open")
    assert test_data[0]["id"] == response_data[0]["id"]
    assert test_data[0]["status"] == response_data[0]["status"]


@pytest.mark.anyio
async def test_spot_orders_invalid_status_422(api_client):
    response = await api_client.post(
        "/spot/orders?currency_pair=BTC_USDT&status=bad",
        json={"key": "kkkkkk", "proxy": None, "secret": "ssssss"},
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_spot_currency_pair_success(monkeypatch, api_client):

    monkeypatch.setattr(spot_view, "create_instanse", fake_spot_create_instance)
    response = await api_client.post(
        "/spot/currency_pair?currency_pair=BTC_USDT",
        json={
            "data": {"limit": 1, "interval": "10s"},
            "security": {"key": "", "proxy": "", "secret": ""},
            "connect": {"read_timeout": 30, "timeout": 5},
        },
    )

    assert response.status_code == 200
    response_data = response.json()
    test_data = await FakeSpot().currency_pair("BTC_USDT")
    assert test_data == response_data


@pytest.mark.anyio
async def test_spot_currency_pair_invalid_status_422(api_client):
    response = await api_client.post(
        "/spot/currency_pair?currenc_pair=BTC_USDT",
        json={
            "data": {"limt": 1, "intrval": "10s"},
            "secuity": {"key": "", "poxy": "", "secret": ""},
            "connct": {"read_timout": 30, "timeout": 5},
        },
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_spot_candlesticks_success(monkeypatch, api_client):

    monkeypatch.setattr(spot_view, "create_instanse", fake_spot_create_instance)
    response = await api_client.post(
        "/spot/candlesticks?currency_pair=BTC_USDT",
        json={
            "data": {"limit": 1, "interval": "10s"},
            "security": {"key": "", "proxy": "", "secret": ""},
            "connect": {"read_timeout": 30, "timeout": 5},
        },
    )

    assert response.status_code == 200
    response_data = response.json()
    test_data = await FakeSpot().list_candlesticks("BTC_USDT", limit=1, interval="10s")
    assert test_data == response_data


@pytest.mark.anyio
async def test_spot_candlesticks_invalid_status_422(api_client):
    response = await api_client.post(
        "/spot/candlesticks?currenc_pair=BTC_USDT",
        json={
            "data": {"limt": 1, "intrval": "10s"},
            "secuity": {"key": "", "poxy": "", "secret": ""},
            "connct": {"read_timout": 30, "timeout": 5},
        },
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_spot_cancel_orders_success(monkeypatch, api_client):

    monkeypatch.setattr(spot_view, "create_instanse", fake_spot_create_instance)
    response = await api_client.post(
        "/spot/cancel_orders?currency_pair=BTC_USDT",
        json={"key": "kkkkkk", "proxy": None, "secret": "ssssss"},
    )

    assert response.status_code == 200
    response_data = response.json()
    test_data = await FakeSpot().cancel_orders("BTC_USDT")
    assert test_data[0].get("order_id") == response_data[0].get("order_id")


@pytest.mark.anyio
async def test_spot_candlesticks_invalid_status_422(api_client):
    response = await api_client.post(
        "/spot/cancel_orders?currenc_pair=BTC_USDT",
        json={"key": "kkkkkk", "proxy": None, "seret": "ssssss"},
    )

    assert response.status_code == 422