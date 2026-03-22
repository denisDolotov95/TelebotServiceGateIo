# -*- coding: utf-8 -*-
import typing

from abc import ABC, abstractmethod

from .model import *

__all__ = [
    "ParseAccountBook",
    "ParseAccounts",
    "ParseCandlesticks",
    "ParseCurrency",
    "ParseCurrencyPair",
    "ParseCurrencyPairs",
    "ParseOpenOrders",
    "ParseOrderBook",
    "ParseOrders",
    "ParseTickers",
    "ParseTotalBalance",
    "ParseTrade",
]


class Parser(ABC):

    def __init__(self, data=None) -> None:

        self.payload = data

    @abstractmethod
    def factory_method(self):

        pass

    def parse(self) -> typing.Any:

        instance = self.factory_method()

        return instance.parse(self.payload)


class Data(ABC):

    @abstractmethod
    def parse(self, payload: typing.Any = None):

        pass


class DataTickers(Data):

    def parse(self, payload: typing.List[dict]) -> typing.List[Ticker]:

        parsed_data = list()
        for data in payload:
            parsed_data.append(Ticker(**data))

        return parsed_data


class ParseTickers(Parser):

    def __init__(self, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

    def factory_method(self) -> DataTickers:

        return DataTickers()


class DataAccount(Data):

    def parse(self, payload: typing.List[dict]) -> typing.List[Account]:

        parsed_data = list()
        for data in payload:
            parsed_data.append(Account(**data))

        return parsed_data


class ParseAccounts(Parser):

    def __init__(self, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

    def factory_method(self) -> DataAccount:

        return DataAccount()


class DataAccountBook(Data):

    def parse(self, payload: typing.List[dict]) -> typing.List[AccountBook]:

        parsed_data = list()
        for data in payload:
            parsed_data.append(AccountBook(**data))

        return parsed_data


class ParseAccountBook(Parser):

    def __init__(self, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

    def factory_method(self) -> DataAccountBook:

        return DataAccountBook()


class DataCurrency(Data):

    def parse(self, payload: dict) -> Currency:

        return Currency(**payload)


class ParseCurrency(Parser):

    def __init__(self, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

    def factory_method(self) -> DataCurrency:

        return DataCurrency()


class DataCurrencyPair(Data):

    def parse(self, payload: dict) -> CurrencyPair:

        return CurrencyPair(**payload)


class ParseCurrencyPair(Parser):

    def __init__(self, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

    def factory_method(self) -> DataCurrencyPair:

        return DataCurrencyPair()


class DataCurrencyPairs(Data):

    def parse(self, payload: typing.List[dict]) -> typing.List[CurrencyPair]:

        parsed_data = list()
        for data in payload:
            parsed_data.append(CurrencyPair(**data))

        return parsed_data


class ParseCurrencyPairs(Parser):

    def __init__(self, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

    def factory_method(self) -> DataCurrencyPairs:

        return DataCurrencyPairs()


class DataTrade(Data):

    def parse(self, payload: typing.List[dict]) -> typing.List[Trade]:

        parsed_data = list()
        for data in payload:
            parsed_data.append(Trade(**data))

        return parsed_data


class ParseTrade(Parser):

    def __init__(self, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

    def factory_method(self) -> DataTrade:

        return DataTrade()


class DataOrderBook(Data):

    def parse(self, payload: dict) -> OrderBook:

        asks = list()
        bids = list()
        for data in payload.get("asks"):
            asks.append(
                Ask(price=data[0], amount=data[1])
                if isinstance(data, list)
                else Ask(price=data.get("price"), amount=data.get("price"))
            )
        for data in payload.get("bids"):
            bids.append(
                Bid(price=data[0], amount=data[1])
                if isinstance(data, list)
                else Bid(price=data.get("price"), amount=data.get("price"))
            )

        return OrderBook(
            id=payload.get("id"),
            current=payload.get("current"),
            update=payload.get("update"),
            asks=asks,
            bids=bids,
        )


class ParseOrderBook(Parser):

    def __init__(self, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

    def factory_method(self) -> DataOrderBook:

        return DataOrderBook()


class DataOrder(Data):

    def parse(self, payload: typing.List[dict]) -> typing.List[Order]:

        parsed_data = list()
        for data in payload:
            parsed_data.append(Order(**data))

        return parsed_data


class ParseOrders(Parser):

    def __init__(self, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

    def factory_method(self) -> DataOrder:

        return DataOrder()


class DataOpenOrder(Data):

    def parse(self, payload: typing.List[dict]) -> typing.List[OpenOrders]:

        parsed_data = list()
        for data in payload:
            orders = list()
            for order in data.get("orders"):
                orders.append(ShortOrder(**order))
            parsed_data.append(
                OpenOrders(
                    currency_pair=data.get("currency_pair"),
                    total=data.get("total"),
                    orders=orders,
                )
            )

        return parsed_data


class ParseOpenOrders(Parser):

    def __init__(self, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

    def factory_method(self) -> DataOpenOrder:

        return DataOpenOrder()


class DataCandlestick(Data):

    def parse(self, payload: typing.List[list]) -> typing.List[Candlestick]:

        parsed_data = list()
        for data in payload:
            parsed_data.append(
                Candlestick(
                    unix_timestamp=data[0],
                    trade_volume_in_quote=data[1],
                    close_price=data[2],
                    highest_price=data[3],
                    lowest_price=data[4],
                    open_price=data[5],
                    trade_volume_in_base=data[6],
                    window_is_closed=data[7],
                )
                if isinstance(data, list)
                else Candlestick(**data)
            )

        return parsed_data


class ParseCandlesticks(Parser):

    def __init__(self, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

    def factory_method(self) -> DataCandlestick:

        return DataCandlestick()


class DataTotalBalance(Data):

    def parse(self, payload: dict) -> TotalBalance:
        get_data = lambda x, key: x.get(key) if x.get(key) else {}
        # `details` / `total` могут отсутствовать в ответе, поэтому аккуратно
        details = payload.get("details") or {}
        class_details = Details(
            cross_margin=CrossMargin(**get_data(details, "cross_margin")),
            spot=Spot(**get_data(details, "spot")),
            finance=Finance(**get_data(details, "finance")),
            margin=Margin(**get_data(details, "margin")),
            quant=Quant(**get_data(details, "quant")),
            futures=Futures(**get_data(details, "futures")),
            delivery=Delivery(**get_data(details, "delivery")),
            warrant=Warrant(**get_data(details, "warrant")),
            cbbc=Cbbc(**get_data(details, "cbbc")),
        )
        total = payload.get("total") or {}
        class_total = Total(
            currency=total.get("currency"),
            amount=total.get("amount"),
            unrealised_pnl=total.get("unrealised_pnl"),
            borrowed=total.get("borrowed"),
        )
        return TotalBalance(
            details=class_details,
            total=class_total,
        )


class ParseTotalBalance(Parser):

    def __init__(self, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

    def factory_method(self) -> DataTotalBalance:

        return DataTotalBalance()
