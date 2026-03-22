# -*- coding: utf-8 -*-
import asyncio
import aiohttp
import pydantic
import logging
import json

from typing import Any, List, Generator
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup

import util

from database import model, request
from gate_wrapper import spot, wallet, parse
from config import (
    Config,
    ConfAlgorithm1,
    ConfAlgorithm2,
    ConfAlgorithm3,
    ConfAlgorithm4,
    ConfAlgorithm5,
    GATE_API_DOMAIN,
)
from telebot_handler import alias


__all__ = [
    "concrete_functor_by",
    "Algorithm1",
    "Algorithm2",
    "Algorithm3",
    "Algorithm4",
    "Algorithm5",
]


def concrete_functor_by(type_algorithm: str | int):

    match int(type_algorithm):
        case 1:
            return Algorithm1(config=ConfAlgorithm1)
        case 2:
            return Algorithm2(config=ConfAlgorithm2)
        case 3:
            return Algorithm3(config=ConfAlgorithm3)
        case 4:
            return Algorithm4(config=ConfAlgorithm4)
        case 5:
            return Algorithm5(config=ConfAlgorithm5)
        case _:
            pass


class Payload(pydantic.BaseModel):

    currency: str = None
    info: str = None
    keyboard: Any = None  # keyboard:telebot.types.InlineKeyboardMarkup


class AsyncAlgorithm(ABC):

    @staticmethod
    async def gate_req(
        url: str,
        # _type: Literal["get", "post"],
        **kwargs,
    ):
        _data = json.dumps(kwargs if kwargs else {})
        payload = {}
        limit_reconnection = 3
        while True and limit_reconnection:
            try:
                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(5 * 30)
                ) as session:
                    logging.info(f"Request to {url}, data: {_data}")
                    async with session.post(
                        url,
                        data=_data,
                        headers={"content-type": "application/json"},
                    ) as response:
                        try:
                            if response.status == 429:
                                logging.info(
                                    f"Too Many Requests to {url}, data: {_data}"
                                )
                                await asyncio.sleep(5)
                                continue
                            payload = await response.json()
                            payload = payload if payload is not None else {}
                        except aiohttp.client_exceptions.ContentTypeError as err:
                            logging.error(f"ContentTypeError occurred for {url}: {err}")
                            logging.error(
                                f"Received Content-Type: {err.headers.get('Content-Type')}"
                            )
                        return payload
            except asyncio.TimeoutError:
                logging.error(f"Timeout from API to {url}, data: {_data}")
                limit_reconnection -= 1
        return payload

    def __init__(
        self,
        config: Config = None,
        gate_req: spot.Spot | wallet.Wallet = None,
        sql_req: request.MyAsyncSession = None,
        cont_filter: util.ContentFilter = util.ContentFilter(),
    ):

        self.config: Config = config
        # self.gate_req: spot.Spot | wallet.Wallet = gate_req
        self.sql_req: request.MyAsyncSession = sql_req
        self.tele_button = util.TelegramButtons
        self.sum_order = util.SumOrderbook
        self.cont_filter: util.ContentFilter = cont_filter
        self.result: Generator | list = []
        self.start_time: datetime = 0
        self.end_time: datetime = 0
        self.delta_time: timedelta = timedelta()
        self.__work_queue = asyncio.Queue()

    def _timer(func):
        async def wrapper(self, *args, **kwargs):
            self.start_time = datetime.now()
            result = await func(self, *args, **kwargs)
            self.end_time = datetime.now()
            self.delta_time = self.end_time - self.start_time
            return result

        return wrapper

    async def _exec_tasks(self) -> list[list]:

        max_cpu = 1
        tasks = [
            asyncio.create_task(util.AsyncTask(self.__work_queue).exec(self._run))
            for _ in range(max_cpu)
            # for _ in range(4)
        ]
        results = await asyncio.gather(*tasks)
        _liset_results = []
        for r in results:
            _liset_results.extend(r)
        return _liset_results

    async def _fill_queue(self):

        accounts = await self.gate_req(f"http://{GATE_API_DOMAIN}/spot/spot_accounts")
        accounts = parse.ParseAccounts(accounts).parse()
        for data in self.cont_filter.filter(accounts):
            await self.__work_queue.put(data)

    @_timer
    async def __call__(self, gen=True):

        await self._fill_queue()
        # task = await asyncio.to_thread(self._exec_tasks)
        # payload = await asyncio.create_task(task)
        payload = await self._exec_tasks()
        self.result = self.generator(payload) if gen else payload
        return self

    @abstractmethod
    async def _run(self, *args, **kwargs) -> list[Payload]:

        pass

    @abstractmethod
    def _info(self, *args, **kwargs) -> str:

        pass

    @abstractmethod
    def _keyboard(self, *args, **kwargs) -> str:

        pass

    async def note(self, currency) -> bool:

        note = await self.sql_req.find_by(model.Note, currency=currency)
        return note

    def generator(self, payload) -> Generator[Any, Any, None]:

        for data in payload:
            yield data


class Algorithm1(AsyncAlgorithm):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

    async def _run(self, data: parse.CurrencyPair):

        first_bar = 0
        candlesticks = await self.gate_req(
            f"http://{GATE_API_DOMAIN}/spot/candlesticks?currency_pair={data.currency}_USDT",
            **{
                "data": {
                    "limit": self.config.bar_limit,
                    "interval": self.config.bar_interval,
                }
            },
        )
        if not candlesticks:
            return
        # candlesticks = candlesticks[::-1]
        second_bar = len(candlesticks) - 1
        delta = util.calculate_delta(
            candlesticks[second_bar].close_price, candlesticks[first_bar].open_price
        )
        _predicat = (
            delta >= self.config.percent
            if self.config.percent > 0
            else delta <= self.config.percent
        )
        # if delta >= self.config.percent:
        if _predicat:
            order_book = await self.gate_req(
                f"http://{GATE_API_DOMAIN}/spot/order_book?currency_pair={data.currency}_USDT",
                **{"data": {"limit": self.config.order_book_limit}},
            )
            tickers = await self.gate_req(
                f"http://{GATE_API_DOMAIN}/spot/tickers?currency_pair={data.currency}_USDT"
            )
            check_note = await self.note(data.base)
            return Payload(
                currency=data.base,
                info=self._info(
                    data,
                    delta,
                    tickers,
                    candlesticks[first_bar],
                    candlesticks[second_bar],
                    len(candlesticks),
                    order_book,
                ),
                keyboard=self._keyboard(data.base, bool(check_note)),
            )

    def _keyboard(self, currency, note_exist=False) -> InlineKeyboardMarkup:

        if self.config.output.type == "message":
            return

        payload = {
            "Update": {
                alias.ACTION: alias.UPDATE_CURRENT,
                alias.ALGORITHM: self.config.id,
                alias.CURRENT: currency,
            },
            "More Info": {
                alias.ACTION: alias.MORE_INFO,
                alias.BACK: alias.UPDATE_CURRENT,
                alias.ALGORITHM: self.config.id,
                alias.CURRENT: currency,
            },
            "List orders": {
                alias.ACTION: alias.LIST_ORDER,
                alias.BACK: alias.UPDATE_CURRENT,
                alias.ALGORITHM: self.config.id,
                alias.CURRENT: currency,
            },
        }
        if note_exist:
            payload["Note"] = {
                alias.ACTION: alias.NOTE,
                alias.BACK: alias.UPDATE_CURRENT,
                alias.ALGORITHM: self.config.id,
                alias.CURRENT: currency,
            }
        buttons = self.tele_button(payload)
        return buttons.create_inline_keyboard(row_width=3)

    def _info(
        self, pair, delta, ticker, first_bar, second_bar, len_candlesticks, order_book
    ):

        new_order_book = self.sum_order(order_book.dict())
        sum_asks = new_order_book.sum("asks")
        sum_bids = new_order_book.sum("bids")
        first_ask = new_order_book.first("asks")
        first_bid = new_order_book.first("bids")
        more_asks = new_order_book.more_then(sum_asks, sum_bids)
        more_bids = new_order_book.more_then(sum_bids, sum_asks)
        return (
            f'\n\n <a href="https://www.gate.io/ru/trade/{pair.id}">{pair.base}</a>'
            + f" | <b>{int(delta)}%</b> (by Algorithm) | <b>{ticker[0].change_percentage}%</b> (in the last 24h)"
            + f"\n\n First open, close price: <b>{first_bar.open_price}</b>, {first_bar.close_price}"
            + f"\n <b>Date: {self.sum_order.s_update_date(first_bar.unix_timestamp)}</b>"
            + f"\n Price volume: {first_bar.trade_volume_in_quote}"
            + f"\n Trade volume: {first_bar.trade_volume_in_base}"
            + f"\n\n Second open, close price: {second_bar.open_price}, <b>{second_bar.close_price}</b>"
            + f"\n <b>Date: {self.sum_order.s_update_date(second_bar.unix_timestamp)}</b>"
            + f"\n Price volume: {second_bar.trade_volume_in_quote}"
            + f"\n Trade volume: {second_bar.trade_volume_in_base}"
            + f"\n\n <b>First / Sum Asks: {first_ask} / {sum_asks} {f'x{more_asks}' if more_asks > more_bids else ''}</b>"
            + f"\n <b>First / Sum Bids: {first_bid} / {sum_bids} {f'x{more_bids}' if more_bids > more_asks else ''}</b>"
            + f"\n Current date: {new_order_book.update_date('current')}"
            + f"\n Update date: {new_order_book.update_date('update')}"
            + f"\n\n Candlesticks (bars): {len_candlesticks}/{self.config.bar_limit}"
        )


class Algorithm2(Algorithm1):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

    async def _run(self, data: parse.CurrencyPair):

        first_bar = 0
        check = lambda x, y: True if x <= y and x >= 0 else False
        candlesticks = await self.gate_req(
            f"http://{GATE_API_DOMAIN}/spot/candlesticks?currency_pair={data.currency}_USDT",
            **{
                "data": {
                    "limit": self.config.bar_limit,
                    "interval": self.config.bar_interval,
                }
            },
        )
        if candlesticks:
            # candlesticks = candlesticks[::-1]
            len_candlesticks = len(candlesticks)
            if self.config.bar_limit != len_candlesticks:
                return
            conv = lambda data: float(data)
            # max_volume = max([i.trade_volume_in_quote for i in candlesticks])
            # limit - 1 - т.к. последний бар динамичный и мало какой информации может представлять
            for i in range(0, self.config.bar_limit - 1):
                first_bar = i
                second_bar = self.config.bar_range + i
                if first_bar >= self.config.bar_limit:
                    break
                if (
                    candlesticks[second_bar].trade_volume_in_quote == 0
                    or candlesticks[first_bar].trade_volume_in_quote == 0
                ):
                    continue
                check_price_volume = conv(
                    candlesticks[first_bar].trade_volume_in_quote
                ) * self.config.price_ratio <= conv(
                    candlesticks[second_bar].trade_volume_in_quote
                )
                delta = util.calculate_delta(
                    candlesticks[second_bar].close_price,
                    candlesticks[first_bar].open_price,
                )
                if check(delta, self.config.percent) and check_price_volume:
                    order_book = await self.gate_req(
                        f"http://{GATE_API_DOMAIN}/spot/order_book?currency_pair={data.currency}_USDT",
                        **{"data": {"limit": self.config.order_book_limit}},
                    )
                    tickers = await self.gate_req(
                        f"http://{GATE_API_DOMAIN}/spot/tickers?currency_pair={data.currency}_USDT"
                    )
                    check_note = await self.note(data.base)
                    return Payload(
                        currency=data.base,
                        info=self._info(
                            data,
                            delta,
                            tickers,
                            candlesticks[first_bar],
                            candlesticks[second_bar],
                            len(candlesticks),
                            order_book,
                        ),
                        keyboard=self._keyboard(data.base, bool(check_note)),
                    )


class Algorithm3(Algorithm1):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

    async def _run(self, data: parse.CurrencyPair):

        extend = self.config.bar_range + 2
        ext_limit = self.config.bar_limit + extend
        check = lambda x, y: True if x <= y and x >= -y else False
        candlesticks = await self.gate_req(
            f"http://{GATE_API_DOMAIN}/spot/candlesticks?currency_pair={data.currency}_USDT",
            **{
                "data": {
                    "limit": self.config.bar_limit,
                    "interval": self.config.bar_interval,
                }
            },
        )
        # candlesticks = candlesticks[::-1]
        if (
            not candlesticks
            or ext_limit != len(candlesticks)
            or not check(
                util.calculate_delta(
                    candlesticks[ext_limit - 1].close_price,
                    candlesticks[0].open_price,
                ),
                self.config.percent,
            )
        ):
            return
        total = 0
        for i in range(0, ext_limit):
            if ext_limit <= extend + i:
                break
            first_bar = i
            second_bar = self.config.bar_range + i
            delta = util.calculate_delta(
                candlesticks[second_bar].close_price,
                candlesticks[first_bar].open_price,
            )
            total += 1 if check(delta, self.config.percent) else 0
        delta = util.calculate_delta(
            candlesticks[ext_limit - 1].close_price, candlesticks[0].open_price
        )
        if total == self.config.bar_limit and delta:
            order_book = await self.gate_req(
                f"http://{GATE_API_DOMAIN}/spot/order_book?currency_pair={data.currency}_USDT",
                **{"data": {"limit": self.config.order_book_limit}},
            )
            order_book = self.sum_order(order_book.dict())
            more_bids = order_book.more_then(
                order_book.sum("bids"), order_book.sum("asks")
            )
            if more_bids and more_bids > self.config.order_book_ratio:
                check_note = await self.note(data.base)
                return Payload(
                    currency=data.base,
                    info=self._info(data, len(candlesticks) - extend, order_book),
                    keyboard=self._keyboard(data.base, bool(check_note)),
                )

    def _info(self, pair, len_candlesticks, order_book: util.SumOrderbook):

        sum_asks = order_book.sum("asks")
        sum_bids = order_book.sum("bids")
        more_asks = order_book.more_then(sum_asks, sum_bids)
        more_bids = order_book.more_then(sum_bids, sum_asks)
        return (
            f'\n\n <a href="https://www.gate.io/ru/trade/{pair.id}">{pair.base}</a>'
            + f"\n\n <b>Sum Asks: {sum_asks} {f'x{more_asks}' if more_asks > more_bids else ''}</b>"
            + f"\n <b>Sum Bids: {sum_bids} {f'x{more_bids}' if more_bids > more_asks else ''}</b>"
            + f"\n Current date: {order_book.update_date('current')}"
            + f"\n Update date: {order_book.update_date('update')}"
            + f"\n\n Candlesticks (bars): {len_candlesticks}/{self.config.bar_limit}"
        )


class Algorithm4(Algorithm1):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

    async def _run(self, data: parse.CurrencyPair) -> List[Payload]:

        candlesticks = await self.gate_req(
            f"http://{GATE_API_DOMAIN}/spot/candlesticks?currency_pair={data.currency}_USDT",
            **{
                "data": {
                    "limit": self.config.bar_limit,
                    "interval": self.config.bar_interval,
                }
            },
        )
        if candlesticks:
            # candlesticks = candlesticks[::-1]
            len_candlesticks = len(candlesticks)
            if self.config.bar_limit != len_candlesticks:
                return
            # candlesticks = candlesticks[::-1]
            conv = lambda data: int(float(data))
            max_trade_volume = max(
                [
                    candlesticks[i].trade_volume_in_base
                    for i in range(0, self.config.bar_limit)
                ]
            )
            # после отработки цикла, последнее значение i сохраняется в памяти
            # и к нему можно обратиться
            for i in range(1, self.config.bar_limit):
                if candlesticks[i].trade_volume_in_base == max_trade_volume:
                    break
            first_bar = i - self.config.bar_range
            second_bar = i
            if (
                conv(candlesticks[second_bar].trade_volume_in_base) <= 0
                or conv(candlesticks[first_bar].trade_volume_in_base) <= 0
            ):
                return
            check_trade_volume = (
                conv(candlesticks[second_bar].trade_volume_in_base)
                >= conv(candlesticks[first_bar].trade_volume_in_base)
                * self.config.trade_ratio
            )
            if check_trade_volume:
                order_book = await self.gate_req(
                    f"http://{GATE_API_DOMAIN}/spot/order_book?currency_pair={data.currency}_USDT",
                    **{"data": {"limit": self.config.order_book_limit}},
                )
                ticker = await self.gate_req(
                    f"http://{GATE_API_DOMAIN}/spot/tickers?currency_pair={data.currency}_USDT"
                )
                check_note = await self.note(data.base)
                return Payload(
                    currency=data.base,
                    info=self._info(
                        data,
                        0,
                        ticker,
                        candlesticks[first_bar],
                        candlesticks[second_bar],
                        len(candlesticks),
                        order_book,
                    ),
                    keyboard=self._keyboard(data.base, bool(check_note)),
                )


class Algorithm5(Algorithm1):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.candle_price = self.config.alias_candle_price[self.config.candle_price]

    def __circular_array(self, dict_candle):

        first_candle_price = dict_candle[0][self.candle_price]
        # last_candle_price = dict_candle[-1][self.candle_price]
        len_candle = len(dict_candle)
        for i in range(len_candle):
            if (
                len(dict_candle[i : self.config.split + i])
                >= self.config.bar_limit / self.config.split
            ):
                temp = dict_candle[i : self.config.split + i]
            else:
                temp = (
                    dict_candle[i : self.config.split + i]
                    + dict_candle[
                        0 : self.config.bar_limit
                        - len(dict_candle[i : self.config.split + i])
                    ]
                )
            total = [
                True
                for candle in temp
                if first_candle_price == candle[self.candle_price]
                # and first_candle_price == last_candle_price
                and candle["open_price"] != candle["close_price"]
            ]
            if (len(total) / self.config.split) * 100 >= self.config.percent:
                return True

    async def _run(self, data: parse.CurrencyPair):
        candlesticks = await self.gate_req(
            f"http://{GATE_API_DOMAIN}/spot/candlesticks?currency_pair={data.currency}_USDT",
            **{
                "data": {
                    "limit": self.config.bar_limit,
                    "interval": self.config.bar_interval,
                }
            },
        )
        if candlesticks:
            # candlesticks = candlesticks[::-1]
            len_candlesticks = len(candlesticks)
            if self.config.bar_limit != len_candlesticks:
                return
            while candlesticks:
                dict_candle = [candle.dict() for candle in candlesticks[:6]]
                del candlesticks[:6]
                if self.__circular_array(dict_candle):
                    order_book = await self.gate_req(
                        f"http://{GATE_API_DOMAIN}/spot/order_book?currency_pair={data.currency}_USDT"
                        **{"data": {"limit": self.config.order_book_limit}},
                    )
                    ticker = await self.gate_req(
                        f"http://{GATE_API_DOMAIN}/spot/tickers?currency_pair={data.currency}_USDT"
                    )
                    check_note = await self.note(data.base)
                    return Payload(
                        currency=data.base,
                        info=self._info(
                            data,
                            ticker,
                            len_candlesticks,
                            order_book,
                        ),
                        keyboard=self._keyboard(data.base, bool(check_note)),
                    )

    def _info(self, pair, ticker, len_candlesticks, order_book):

        new_order_book = self.sum_order(order_book.dict())
        sum_asks = new_order_book.sum("asks")
        sum_bids = new_order_book.sum("bids")
        more_asks = new_order_book.more_then(sum_asks, sum_bids)
        more_bids = new_order_book.more_then(sum_bids, sum_asks)
        return (
            f'\n\n <a href="https://www.gate.io/ru/trade/{pair.id}">{pair.base}</a>'
            + f" | <b>-</b> (by Algorithm) | <b>{ticker[0].change_percentage}%</b> (in the last 24h)"
            + f"\n\n <b>Sum Asks: {sum_asks} {f'x{more_asks}' if more_asks > more_bids else ''}</b>"
            + f"\n <b>Sum Bids: {sum_bids} {f'x{more_bids}' if more_bids > more_asks else ''}</b>"
            + f"\n Current date: {new_order_book.update_date('current')}"
            + f"\n Update date: {new_order_book.update_date('update')}"
            + f"\n\n Candlesticks (bars): {len_candlesticks}/{self.config.bar_limit}"
        )
