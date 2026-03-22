# -*- coding: utf-8 -*-
import re
import telebot
import pytest

from typing import Any
from prettytable import PrettyTable

from .. import util


class TestUtil:

    @pytest.fixture(scope="class")
    def example(self) -> list[list[str, Any]]:

        return [
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

    @pytest.fixture(scope="class")
    def example_2(self) -> dict[str, Any]:

        return {
            "one": {"info": ""},
            "two": {"info": ""},
            "three": {"info": ""},
            "four": {
                "one": "",
                "commands": {
                    "one": {"info": ""},
                    "two": {"info": ""},
                    "three": {"info": ""},
                },
            },
        }

    def test_calculate_delta(self, example):

        returned = util.calculate_delta(example[0][5], example[1][5])
        assert isinstance(returned, float)


class TestTable:

    @pytest.fixture(scope="class")
    def example(self) -> list[list[str, Any]]:

        return [
            {
                "currency": "ZOON",
                "available": "0.000000002545",
                "locked": "9717",
                "update_id": None,
            }
        ]

    def test_get_string(self, example):

        for data in example:
            text = util.Table(data, pretty=PrettyTable(header=False)).get_string(
                total_items_row=4
            )
            assert isinstance(text, str)
            assert (
                text
                == """<pre>+-----------+----------------+---------+------------+
| currency: |   available:   | locked: | update_id: |
|    ZOON   | 0.000000002545 |   9717  |    None    |
+-----------+----------------+---------+------------+</pre>"""
            )


class TelegramButtons:

    @pytest.fixture(scope="class")
    def example(self) -> dict[str, Any]:

        return {"example": {"example": "example"}}

    @pytest.fixture(scope="class")
    def example_2(self) -> list[str, Any]:

        return [r"\test", r"\test2"]

    def test_create_inline_keyboard(self, example):

        instance = util.TelegramButtons(example)
        returned = instance.create_inline_keyboard()
        assert isinstance(returned, telebot.types.InlineKeyboardMarkup)
        assert isinstance(instance.payload, example)
        for data in instance.buttons:
            assert isinstance(data, telebot.types.InlineKeyboardButton)

    def test_create_reply_keyboard(self, example):

        instance = util.TelegramButtons(example)
        returned = instance.create_reply_keyboard()
        assert isinstance(returned, telebot.types.ReplyKeyboardMarkup)
        assert isinstance(instance.payload, example)
        for data in instance.buttons:
            assert isinstance(data, telebot.types.KeyboardButton)


class TestSumOrderbook:

    @pytest.fixture(scope="class")
    def example(self) -> list[dict[str, Any]]:

        data = [
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

        return data

    def test_sum(self, example):

        for data in example:
            instance = util.SumOrderbook(data)
            for key in ["asks", "bids"]:
                sum = instance.sum(key)
                assert isinstance(sum, float | int)

    def test_more_then(self, example):

        for data in example:
            instance = util.SumOrderbook(data)
            sum_asks = instance.sum("asks")
            sum_bids = instance.sum("bids")
            assert isinstance(instance.more_then(sum_asks, sum_bids), float | int)
            assert isinstance(instance.more_then(sum_bids, sum_asks), float | int)

    def test_update_date(self, example):

        for data in example:
            instance = util.SumOrderbook(data)
            regex = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
            for key in ["current", "update"]:
                assert bool(
                    re.match(
                        regex,
                        instance.update_date(key),
                    )
                )
                assert bool(
                    re.match(
                        regex,
                        instance.s_update_date(str(data[key])[:-3]),
                    )
                )


class TestContentFilter:

    @pytest.fixture(scope="class")
    def example(self) -> list[dict[str, Any]]:

        data = [
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
            },
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
            },
        ]

        return [
            {
                "example": data,
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
                "returned": [data[0]],
            },
            {
                "example": data,
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

    def test_filter(self, example):

        for data in example:
            instance = util.ContentFilter(data["filters"])
            result = instance.filter(data["example"])
            assert len(result) == len(data["returned"]) and result == data["returned"]
