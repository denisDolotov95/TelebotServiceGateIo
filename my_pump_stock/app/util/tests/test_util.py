# -*- coding: utf-8 -*-
import re
import telebot
import pytest

from prettytable import PrettyTable

from .. import util


class TestUtil:

    @pytest.mark.usefixtures("data_util_calculate_delta")
    def test_calculate_delta(self, data_util_calculate_delta):

        returned = util.calculate_delta(
            data_util_calculate_delta[0][5], data_util_calculate_delta[1][5]
        )
        assert isinstance(returned, float)


@pytest.mark.usefixtures("data_table")
class TestTable:

    def test_get_string(self, data_table):

        text = util.Table(
            data_table["example"], pretty=PrettyTable(header=False)
        ).get_string(total_items_row=4)
        assert isinstance(text, str)
        print(text)
        assert text == data_table["return_text"]


class TestTelegramButtons:

    @pytest.mark.usefixtures("data_telegram_buttons")
    def test_create_inline_keyboard(self, data_telegram_buttons):

        instance = util.TelegramButtons(data_telegram_buttons)
        returned = instance.create_inline_keyboard()
        assert isinstance(returned, telebot.types.InlineKeyboardMarkup)
        for data in instance.buttons:
            assert isinstance(data, telebot.types.InlineKeyboardButton)

    @pytest.mark.usefixtures("data_reply_keyboard")
    def test_create_reply_keyboard(self, data_reply_keyboard):

        instance = util.TelegramButtons(data_reply_keyboard)
        returned = instance.create_reply_keyboard()
        assert isinstance(returned, telebot.types.ReplyKeyboardMarkup)
        for data in instance.buttons:
            assert isinstance(data, telebot.types.KeyboardButton)


@pytest.mark.usefixtures("data_sum_order_book")
class TestSumOrderbook:

    def test_sum(self, data_sum_order_book):

        instance = util.SumOrderbook(data_sum_order_book)
        for key in ["asks", "bids"]:
            sum = instance.sum(key)
            assert isinstance(sum, float | int)

    def test_more_then(self, data_sum_order_book):

        instance = util.SumOrderbook(data_sum_order_book)
        sum_asks = instance.sum("asks")
        sum_bids = instance.sum("bids")
        assert isinstance(instance.more_then(sum_asks, sum_bids), float | int)
        assert isinstance(instance.more_then(sum_bids, sum_asks), float | int)

    def test_update_date(self, data_sum_order_book):

        instance = util.SumOrderbook(data_sum_order_book)
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
                    instance.s_update_date(str(data_sum_order_book[key])[:-3]),
                )
            )


@pytest.mark.usefixtures("data_content_filter")
class TestContentFilter:

    def test_filter(self, data_content_filter):

        instance = util.ContentFilter(data_content_filter["filters"])
        result = instance.filter(data_content_filter["example"])
        assert (
            len(result) == len(data_content_filter["returned"])
            and result == data_content_filter["returned"]
        )
