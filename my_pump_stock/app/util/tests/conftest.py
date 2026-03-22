# -*- coding: utf-8 -*-
import pytest


@pytest.fixture(
    params=[
        [
            [
                "1539852480",
                "971519.677",
                "0.0023724",
                "0.0023922",
                "0.0023724",
                "0.0023737",
                "true",
            ],
            [
                "1539852478",
                "971519.677",
                "0.0021724",
                "0.0021922",
                "0.0021724",
                "0.0021737",
                "true",
            ],
        ]
    ]
)
def data_util_calculate_delta(request):
    """Параметры для работы с классом util.calculate_delta

    Args:
        request (_type_): контекст фикстуры

    Yields:
        _type_: _description_
    """
    param = request.param
    yield param


@pytest.fixture(
    params=[
        {
            "example": {
                "currency": "ZOON",
                "available": "0.000000002545",
                "locked": "9717",
                "update_id": None,
            },
            "return_text": """<pre>+-----------+----------------+---------+------------+
| currency: |   available:   | locked: | update_id: |
|    ZOON   | 0.000000002545 |   9717  |    None    |
+-----------+----------------+---------+------------+</pre>""",
        },
        {
            "example": {
                "currency": "BTC",
                "available": "0.1",
                "locked": "1",
                "update_id": None,
            },
            "return_text": """<pre>+-----------+------------+---------+------------+
| currency: | available: | locked: | update_id: |
|    BTC    |    0.1     |    1    |    None    |
+-----------+------------+---------+------------+</pre>""",
        },
    ]
)
def data_table(request):
    """Параметры для работы с классом util.Table

    Args:
        request (_type_): контекст фикстуры

    Yields:
        _type_: _description_
    """
    param = request.param
    yield param


@pytest.fixture(
    params=[
        {
            "example": [
                {
                    "id": "10SET_USDT",
                    "base": "10SET",
                    "quote": "USDT",
                    "fee": "0.2",
                    "min_base_amount": "0.01",
                    "min_quote_amount": "10",
                    "max_base_amount": None,
                    "max_quote_amount": "5000000",
                    "amount_precision": 2,
                    "precision": 4,
                    "trade_status": "tradable",
                    "sell_start": 1607313600,
                    "buy_start": 1622433600,
                }
            ],
            "filters": [
                lambda x: (
                    x.get("id") == "10SET_USDT"
                    and x.get("base") == "10SET"
                    and x.get("quote") == "USDT"
                    and x.get("fee") == "0.2"
                    and x.get("min_base_amount") == "0.01"
                    and x.get("min_quote_amount") == "10"
                    and x.get("max_base_amount") == None
                ),
                lambda x: (
                    x.get("max_quote_amount") == "5000000"
                    and x.get("amount_precision") == 2
                    and x.get("precision") == 4
                    and x.get("trade_status") == "tradable"
                    and x.get("sell_start") == 1607313600
                    and x.get("buy_start") == 1622433600
                ),
            ],
            "returned": [
                {
                    "id": "10SET_USDT",
                    "base": "10SET",
                    "quote": "USDT",
                    "fee": "0.2",
                    "min_base_amount": "0.01",
                    "min_quote_amount": "10",
                    "max_base_amount": None,
                    "max_quote_amount": "5000000",
                    "amount_precision": 2,
                    "precision": 4,
                    "trade_status": "tradable",
                    "sell_start": 1607313600,
                    "buy_start": 1622433600,
                }
            ],
        },
        {
            "example": [
                {
                    "id": "4TOKEN_USDT",
                    "base": "4TOKEN",
                    "quote": "USDT",
                    "fee": "0.2",
                    "min_base_amount": "1",
                    "min_quote_amount": "10",
                    "max_base_amount": None,
                    "max_quote_amount": "5000000",
                    "amount_precision": 0,
                    "precision": 8,
                    "trade_status": "tradable",
                    "sell_start": 1607313600,
                    "buy_start": 1685260800,
                }
            ],
            "filters": [
                lambda x: (
                    x.get("id") != "4TOKEN_USDT"
                    and x.get("base") != "4TOKEN"
                    and x.get("quote") != "USDT"
                    and x.get("fee") != "0.2"
                    and x.get("min_base_amount") != "1"
                    and x.get("min_quote_amount") != "10"
                    and x.get("max_base_amount") != None
                ),
                lambda x: (
                    x.get("max_quote_amount") != "5000000"
                    and x.get("amount_precision") != 0
                    and x.get("precision") != 8
                    and x.get("trade_status") != "tradable"
                    and x.get("sell_start") != 1607313600
                    and x.get("buy_start") != 1685260800
                ),
            ],
            "returned": [],
        },
    ]
)
def data_content_filter(request):
    """Параметры для работы с классом util.ContentFilter

    Args:
        request (_type_): контекст фикстуры

    Yields:
        _type_: _description_
    """
    param = request.param
    yield param


@pytest.fixture(
    params=[
        {
            "id": None,
            "current": 1713902908608,
            "update": 1713902908608,
            "asks": [
                {"price": "66237.7", "amount": "0.98385"},
                {"price": "66239.7", "amount": "0.002"},
                {"price": "66241", "amount": "0.52"},
                {"price": "66241.5", "amount": "0.52"},
                {"price": "66241.6", "amount": "0.05442"},
                {"price": "66241.9", "amount": "0.0018"},
                {"price": "66243.4", "amount": "0.24986"},
                {"price": "66243.5", "amount": "0.2437"},
                {"price": "66244", "amount": "0.0015"},
                {"price": "66244.1", "amount": "0.11844"},
            ],
            "bids": [
                {"price": "66237.6", "amount": "1.58799"},
                {"price": "66236.6", "amount": "0.00169"},
                {"price": "66233.4", "amount": "0.2437"},
                {"price": "66230.3", "amount": "0.29437"},
                {"price": "66230.2", "amount": "0.52709"},
                {"price": "66230.1", "amount": "0.2437"},
                {"price": "66229.6", "amount": "0.06222"},
                {"price": "66226.9", "amount": "0.03738"},
                {"price": "66226.5", "amount": "0.002"},
                {"price": "66226.4", "amount": "0.06222"},
            ],
        },
        {
            "id": None,
            "current": 1713196929916,
            "update": 1710987115835,
            "asks": [],
            "bids": [],
        },
    ]
)
def data_sum_order_book(request):
    """Параметры для работы с классом util.SumOrderbook

    Args:
        request (_type_): контекст фикстуры

    Yields:
        _type_: _description_
    """
    param = request.param
    yield param


@pytest.fixture(params=[{"example": {"example": "example"}}])
def data_telegram_buttons(request):
    """Параметры для кнопок в сообщении telegram

    Args:
        request (FixtureRequest): контекст фикстуры

    Returns:
        _type_: _description_
    """
    param = request.param
    yield param


@pytest.fixture(params=[[r"\test", r"\test2"]])
def data_reply_keyboard(request):
    """Параметры для проверки создания
    кнопок в главном окне чата telegram

    Args:
        request (FixtureRequest):  контекст фикстуры

    Returns:
        _type_: _description_
    """
    param = request.param
    yield param