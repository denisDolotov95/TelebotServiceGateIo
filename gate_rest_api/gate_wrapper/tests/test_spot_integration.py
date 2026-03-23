# -*- coding: utf-8 -*-
import pytest

from gate_wrapper.model import *


@pytest.mark.asyncio
@pytest.mark.usefixtures("spot_instance")
class TestAsyncSpot:
    """Integration tests with service gate.io"""

    example = "BTC_USDT"

    async def test_async_currency_pair(self, spot_instance):
        for async_req in {False, True}:
            response = await spot_instance.currency_pair(
                currency_pair=self.example,
                async_req=async_req,
                _request_timeout=(5, 5),
            )
            assert isinstance(response, CurrencyPair)

    async def test_async_list_orders(self, spot_instance):

        for async_req in {False, True}:
            response = await spot_instance.list_orders(
                currency_pair=self.example,
                status="open",
                async_req=async_req,
                _request_timeout=(5, 5),
            )
            assert isinstance(response, list)
            assert all(isinstance(i, Order) for i in response)

    async def test_async_spot_accounts(self, spot_instance):

        for async_req in {False, True}:
            response = await spot_instance.list_spot_accounts(
                async_req=async_req, _request_timeout=(5, 5)
            )
            assert isinstance(response, list)
            assert all(isinstance(i, Account) for i in response)

    async def test_async_spot_account_book(self, spot_instance):

        for async_req in {False, True}:
            response = await spot_instance.list_spot_account_book(
                async_req=async_req, _request_timeout=(5, 5)
            )
            assert isinstance(response, list)
            assert all(isinstance(i, AccountBook) for i in response)

    async def test_async_trades(self, spot_instance):

        for async_req in {False, True}:
            response = await spot_instance.list_trades(
                currency_pair=self.example,
                async_req=async_req,
                _request_timeout=(5, 5),
            )
            assert isinstance(response, list)
            assert all(isinstance(i, Trade) for i in response)

    async def test_async_order_book(self, spot_instance):

        for async_req in {False, True}:
            response = await spot_instance.order_book(
                currency_pair=self.example,
                async_req=async_req,
                _request_timeout=(5, 5),
            )
            assert isinstance(response, OrderBook)

    async def test_async_all_open_orders(self, spot_instance):

        for async_req in {False, True}:
            response = await spot_instance.list_all_open_orders(
                async_req=async_req, _request_timeout=(5, 5)
            )
            assert isinstance(response, list)
            assert all(isinstance(i, OpenOrders) for i in response)

    async def test_async_candlesticks(self, spot_instance):

        for async_req in {False, True}:
            response = await spot_instance.list_candlesticks(
                currency_pair=self.example,
                async_req=async_req,
                _request_timeout=(5, 5),
            )
            assert isinstance(response, list)
            assert all(isinstance(i, Candlestick) for i in response)
