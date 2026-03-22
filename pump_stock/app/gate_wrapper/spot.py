# -*- coding: utf-8 -*-
import gate_api

from .parse import (
    Account,
    Order,
    ParseOrders,
    ParseAccounts,
    AccountBook,
    ParseAccountBook,
    CurrencyPair,
    ParseCurrencyPair,
    ParseCandlesticks,
    Candlestick,
    ParseOpenOrders,
    ParseCurrencyPairs,
    OpenOrders,
    ParseOrderBook,
    OrderBook,
    Ticker,
    ParseTickers,
    Trade,
    ParseTrade,
)
from .util import processing

__all__ = ["Spot"]


class Spot:

    __async_to_thread = True

    def __init__(
        self, api_client: gate_api.ApiClient, instance: gate_api.SpotApi = None
    ) -> None:
        self.spot_api_instance = (
            instance if instance is not None else gate_api.SpotApi(api_client)
        )

    @processing(async_task=__async_to_thread)
    def currency_pair(self, *args, **kwargs) -> CurrencyPair:
        """https://www.gate.io/docs/developers/apiv4/en/#get-details-of-a-specific-currency

        Returns:
            dict: _description_
        """
        # Get details of a specifc currency pair
        api_response = self.spot_api_instance.get_currency_pair(*args, **kwargs)
        return ParseCurrencyPair(
            api_response.get().to_dict()
            if kwargs.get("async_req")
            else api_response.to_dict()
        ).parse()

    @processing(async_task=__async_to_thread)
    def cancel_orders(self, *args, **kwargs) -> list:
        """https://www.gate.io/docs/developers/apiv4/en/#cancel-all-open-orders-in-specified-currency-pair

        Returns:
            list[Order]: _description_
        """
        api_response = self.spot_api_instance.cancel_orders(*args, **kwargs)
        cancel_orders = list()
        for data in api_response.get() if kwargs.get("async_req") else api_response:
            cancel_orders.append(data.to_dict())
        return ParseOrders(cancel_orders).parse()

    @processing(async_task=__async_to_thread)
    def list_orders(self, *args, **kwargs) -> list[Order]:
        """https://www.gate.io/docs/developers/apiv4/en/#list-orders

        Returns:
            list[Order]: _description_
        """
        api_response = self.spot_api_instance.list_orders(*args, **kwargs)
        list_orders = list()
        for data in api_response.get() if kwargs.get("async_req") else api_response:
            list_orders.append(data.to_dict())
        return ParseOrders(list_orders).parse()

    @processing(async_task=__async_to_thread)
    def list_tickers(self, *args, **kwargs) -> list[Ticker]:
        """https://www.gate.io/docs/developers/apiv4/en/#get-details-of-a-specifc-currency-pair

        Returns:
            list[Ticker]: _description_
        """
        api_response = self.spot_api_instance.list_tickers(*args, **kwargs)
        tickers = list()
        for data in api_response.get() if kwargs.get("async_req") else api_response:
            tickers.append(data.to_dict())
        return ParseTickers(tickers).parse()

    @processing(async_task=__async_to_thread)
    def list_currency_pairs(self, *args, **kwargs) -> list[CurrencyPair]:
        """https://www.gate.io/docs/developers/apiv4/en/#list-all-currency-pairs-supported

        Returns:
            list[CurrencyPair]: _description_
        """
        api_response = self.spot_api_instance.list_currency_pairs(*args, **kwargs)
        pairs = list()
        for data in api_response.get() if kwargs.get("async_req") else api_response:
            pairs.append(data.to_dict())
        return ParseCurrencyPairs(pairs).parse()

    @processing(async_task=__async_to_thread)
    def list_spot_accounts(self, *args, **kwargs) -> list[Account]:
        """https://www.gate.io/docs/developers/apiv4/en/#list-spot-accounts

        Returns:
            list[Account]: _description_
        """
        api_response = self.spot_api_instance.list_spot_accounts(*args, **kwargs)
        spot_accounts = list()
        for data in api_response.get() if kwargs.get("async_req") else api_response:
            spot_accounts.append(data.to_dict())
        return ParseAccounts(spot_accounts).parse()

    @processing(async_task=__async_to_thread)
    def list_spot_account_book(self, *args, **kwargs) -> list[AccountBook]:
        """https://www.gate.io/docs/developers/apiv4/en/#query-account-book

        Returns:
            list[AccountBook]: _description_
        """
        # List all spot accounts
        api_response = self.spot_api_instance.list_spot_account_book(*args, **kwargs)
        spot_account_book = list()
        for data in api_response.get() if kwargs.get("async_req") else api_response:
            spot_account_book.append(data.to_dict())
        return ParseAccountBook(spot_account_book).parse()

    @processing(async_task=__async_to_thread)
    def list_trades(self, *args, **kwargs) -> list[Trade]:
        """https://www.gate.io/docs/developers/apiv4/en/#retrieve-market-trades

        Returns:
            list[Trade]: _description_
        """
        api_response = self.spot_api_instance.list_trades(*args, **kwargs)
        trades = list()
        for data in api_response.get() if kwargs.get("async_req") else api_response:
            trades.append(data.to_dict())
        return ParseTrade(trades).parse()

    @processing(async_task=__async_to_thread)
    def order_book(self, *args, **kwargs) -> OrderBook:
        """https://www.gate.io/docs/developers/apiv4/en/#retrieve-order-book

        Returns:
            OrderBook: _description_
        """
        # List all spot accounts
        api_response = self.spot_api_instance.list_order_book(*args, **kwargs)
        return ParseOrderBook(
            api_response.get().to_dict()
            if kwargs.get("async_req")
            else api_response.to_dict()
        ).parse()

    @processing(async_task=__async_to_thread)
    def list_all_open_orders(self, *args, **kwargs) -> list[OpenOrders]:
        """https://www.gate.io/docs/developers/apiv4/en/#list-all-open-orders

        Returns:
            list[OpenOrders]: _description_
        """
        api_response = self.spot_api_instance.list_all_open_orders(*args, **kwargs)
        all_open_orders = list()
        for data in api_response.get() if kwargs.get("async_req") else api_response:
            all_open_orders.append(data.to_dict())
        return ParseOpenOrders(all_open_orders).parse()

    @processing(async_task=__async_to_thread)
    def list_candlesticks(self, *args, **kwargs) -> list[Candlestick]:
        """https://www.gate.io/docs/developers/apiv4/en/#market-candlesticks

        Returns:
            list[Candlestick]: _description_
        """
        api_response = self.spot_api_instance.list_candlesticks(*args, **kwargs)
        return ParseCandlesticks(
            api_response.get() if kwargs.get("async_req") else api_response
        ).parse()