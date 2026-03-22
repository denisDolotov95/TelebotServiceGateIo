import pytest

from ..model import (
    Ticker,
    OrderBook,
    Ask,
    Bid,
    Candlestick,
    TotalBalance,
    Details,
    Total,
)
from ..parse import (
    ParseTickers,
    ParseOrderBook,
    ParseCandlesticks,
    ParseTotalBalance,
)


def test_parse_tickers():
    payload = [
        {
            "currency_pair": "BTC_USDT",
            "last": "50000",
            "lowest_ask": "50010",
            "highest_bid": "49990",
        }
    ]

    result = ParseTickers(payload).parse()

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], Ticker)
    assert result[0].currency_pair == "BTC_USDT"
    assert result[0].last == "50000"


def test_parse_order_book():
    payload = {
        "id": 1,
        "current": 100,
        "update": 101,
        "asks": [["50000", "1.0"]],
        "bids": [["49900", "2.0"]],
    }

    result = ParseOrderBook(payload).parse()

    assert isinstance(result, OrderBook)
    assert result.id == 1
    assert result.current == 100
    assert result.update == 101
    assert len(result.asks) == 1
    assert len(result.bids) == 1
    assert isinstance(result.asks[0], Ask)
    assert isinstance(result.bids[0], Bid)
    assert result.asks[0].price == "50000"
    assert result.bids[0].amount == "2.0"


def test_parse_candlesticks():
    payload = [
        [
            "1630000000",
            10.0,
            "50000",
            "51000",
            "49000",
            "49500",
            0.5,
            True,
        ]
    ]

    result = ParseCandlesticks(payload).parse()

    assert isinstance(result, list)
    assert len(result) == 1
    cs = result[0]
    assert isinstance(cs, Candlestick)
    assert cs.unix_timestamp == "1630000000"
    assert cs.trade_volume_in_quote == 10.0
    assert cs.open_price == "49500"
    assert cs.window_is_closed is True


def test_parse_total_balance_with_minimal_payload():
    payload = {
        "details": {
            "spot": {
                "currency": "USDT",
                "amount": "100.0",
            }
        },
        "total": {
            "currency": "USDT",
            "amount": "100.0",
        },
    }

    result = ParseTotalBalance(payload).parse()

    assert isinstance(result, TotalBalance)
    assert isinstance(result.details, Details)
    assert isinstance(result.total, Total)
    assert result.details.spot.currency == "USDT"
    assert result.details.spot.amount == "100.0"
    assert result.total.currency == "USDT"
    assert result.total.amount == "100.0"


def test_parse_total_balance_with_empty_sections():
    # должно работать даже если details/total частично или полностью пустые
    payload = {
        "details": {},
        "total": {},
    }

    result = ParseTotalBalance(payload).parse()

    assert isinstance(result, TotalBalance)
    assert isinstance(result.details, Details)
    assert isinstance(result.total, Total)