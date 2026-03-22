# -*- coding: utf-8 -*-
import pytest
import asyncio

from ..model import *


@pytest.mark.usefixtures("instance_spot")
class TestAsyncSpot:
    """Integration tests with service gate.io"""

    example = "BTC_USDT"

    event_loop = asyncio.new_event_loop()

    asyncio.set_event_loop(event_loop)

    def test_async_currency_pair(self, instance_spot):
        for async_req in {False, True}:
            response = self.event_loop.run_until_complete(
                instance_spot.currency_pair(
                    currency_pair=self.example, async_req=async_req
                )
            )
            assert isinstance(response, CurrencyPair)

    def test_async_list_orders(self, instance_spot):

        for async_req in {False, True}:
            response = self.event_loop.run_until_complete(
                instance_spot.list_orders(
                    currency_pair=self.example, status="open", async_req=async_req
                )
            )
            assert isinstance(response, list)
            assert all(isinstance(i, Order) for i in response)

    def test_async_spot_accounts(self, instance_spot):

        for async_req in {False, True}:
            response = self.event_loop.run_until_complete(
                instance_spot.list_spot_accounts(async_req=async_req)
            )
            assert isinstance(response, list)
            assert all(isinstance(i, Account) for i in response)

    def test_async_spot_account_book(self, instance_spot):

        for async_req in {False, True}:
            response = self.event_loop.run_until_complete(
                instance_spot.list_spot_account_book(async_req=async_req)
            )
            assert isinstance(response, list)
            assert all(isinstance(i, AccountBook) for i in response)

    def test_async_trades(self, instance_spot):

        for async_req in {False, True}:
            response = self.event_loop.run_until_complete(
                instance_spot.list_trades(
                    currency_pair=self.example, async_req=async_req
                )
            )
            assert isinstance(response, list)
            assert all(isinstance(i, Trade) for i in response)

    def test_async_order_book(self, instance_spot):

        for async_req in {False, True}:
            response = self.event_loop.run_until_complete(
                instance_spot.order_book(
                    currency_pair=self.example, async_req=async_req
                )
            )
            assert isinstance(response, OrderBook)

    def test_async_all_open_orders(self, instance_spot):

        for async_req in {False, True}:
            response = self.event_loop.run_until_complete(
                instance_spot.list_all_open_orders(async_req=async_req)
            )
            assert isinstance(response, list)
            assert all(isinstance(i, OpenOrders) for i in response)

    def test_async_candlesticks(self, instance_spot):

        for async_req in {False, True}:
            response = self.event_loop.run_until_complete(
                instance_spot.list_candlesticks(
                    currency_pair=self.example, async_req=async_req
                )
            )
            assert isinstance(response, list)
            assert all(isinstance(i, Candlestick) for i in response)
