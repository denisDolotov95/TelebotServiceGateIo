# -*- coding: utf-8 -*-
import asyncio
import aiohttp
import multiprocessing
import pydantic
import logging
import json

from typing import Any, Generator
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import util

from gate_wrapper import model as g_model, parse

from database import model as d_model, request
from config import Config, ConfAlgorithm1, ConfAlgorithm2, GATE_API_DOMAIN
from telebot_handler import alias


__all__ = ["concrete_functor_by", "Algorithm1", "Algorithm2"]


def concrete_functor_by(type_algorithm: str | int):

    match int(type_algorithm):
        case 1:
            return Algorithm1(config=ConfAlgorithm1())
        case 2:
            return Algorithm2(config=ConfAlgorithm2())
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
        # gate_req: spot.Spot | wallet.Wallet = None,
        sql_req: request.MyAsyncSession = None,
        cont_filter: util.ContentFilter = None,
    ):

        self.config: Config = config
        # self.gate_req: spot.Spot | wallet.Wallet = gate_req
        self.sql_req: request.MyAsyncSession = sql_req
        self.tele_button = util.TelegramButtons
        self.sum_order = util.SumOrderbook
        self.cont_filter: util.ContentFilter = (
            cont_filter if cont_filter else util.ContentFilter()
        )
        self.result: Generator | None = None
        self.start_time: datetime = 0
        self.end_time: datetime = 0
        self.delta_time: timedelta = 0
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

        max_cpu = multiprocessing.cpu_count()
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

        note = await self.sql_req.find_by(d_model.Note, currency=currency)
        return note

    def generator(self, payload) -> Generator[Any, Any, None]:
        for data in payload:
            yield data


class Algorithm1(AsyncAlgorithm):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

    async def _run(self, data: g_model.Account) -> None | Payload:

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
        candlesticks = parse.ParseCandlesticks(candlesticks).parse()
        second_bar = len(candlesticks) - 1
        delta = util.calculate_delta(
            candlesticks[second_bar].close_price, candlesticks[first_bar].open_price
        )
        _predicat = (
            delta >= self.config.percent
            if self.config.percent > 0
            else delta <= self.config.percent
        )
        if _predicat:
            order_book = await self.gate_req(
                f"http://{GATE_API_DOMAIN}/spot/order_book?currency_pair={data.currency}_USDT",
                **{"data": {"limit": self.config.order_book_limit}},
            )
            tickers = await self.gate_req(
                f"http://{GATE_API_DOMAIN}/spot/tickers?currency_pair={data.currency}_USDT"
            )
            check_note = await self.note(data.currency)
            return Payload(
                currency=data.currency,
                info=self._info(
                    data,
                    delta,
                    parse.ParseTickers(tickers).parse(),
                    candlesticks[first_bar],
                    candlesticks[second_bar],
                    len(candlesticks),
                    parse.ParseOrderBook(order_book).parse(),
                ),
                keyboard=self._keyboard(data.currency, bool(check_note)),
            )

    def _keyboard(self, currency, note_exist=False) -> str:

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
        self,
        account,
        delta,
        ticker,
        first_bar,
        second_bar,
        len_candlesticks,
        order_book,
    ):

        new_order_book = self.sum_order(order_book.dict())
        sum_asks = new_order_book.sum("asks")
        sum_bids = new_order_book.sum("bids")
        first_ask = new_order_book.first("asks")
        first_bid = new_order_book.first("bids")
        more_asks = new_order_book.more_then(sum_asks, sum_bids)
        more_bids = new_order_book.more_then(sum_bids, sum_asks)

        return (
            f'\n\n <a href="https://www.gate.io/ru/trade/{account.currency}_USDT">{account.currency}</a>'
            + f" | <b>{int(delta)}%</b> (by algorithm) | <b>{ticker[0].change_percentage}%</b> (in the last 24h)"
            + f"\n\n Available amount , total price: {round(float(account.available), 3)}, "
            + f"<b>{round(float(account.available) * float(ticker[0].last), 3)} {ticker[0].currency_pair.split('_')[1]}</b>"
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

    async def _run(self, data: g_model.Account) -> Payload | None:

        order_book = await self.gate_req(
            f"http://{GATE_API_DOMAIN}/spot/order_book?currency_pair={data.currency}_USDT",
            **{"data": {"limit": self.config.order_book_limit}},
        )
        order_book = self.sum_order(order_book.dict())
        sum_asks = order_book.sum("asks")
        sum_bids = order_book.sum("bids")
        more_asks = order_book.more_then(sum_asks, sum_bids)
        more_bids = order_book.more_then(sum_bids, sum_asks)
        if more_asks > more_bids:
            tickers = await self.gate_req(
                f"http://{GATE_API_DOMAIN}/spot/tickers?currency_pair={data.currency}_USDT"
            )
            check_note = await self.note(data.currency)
            return Payload(
                currency=data.currency,
                info=self._info(data, parse.ParseTickers(tickers).parse(), order_book),
                keyboard=self._keyboard(data.currency, bool(check_note)),
            )

    def _info(self, account, ticker, order_book):

        sum_asks = order_book.sum("asks")
        sum_bids = order_book.sum("bids")
        more_asks = order_book.more_then(sum_asks, sum_bids)
        more_bids = order_book.more_then(sum_bids, sum_asks)
        return (
            f'\n\n <a href="https://www.gate.io/ru/trade/{account.currency}_USDT">{account.currency}</a>'
            + f" | <b>-</b> (by algorithm) | <b>{ticker[0].change_percentage}%</b> (in the last 24h)"
            + f"\n\n <b>Sum Asks: {sum_asks} {f'x{more_asks}' if more_asks > more_bids else ''}</b>"
            + f"\n <b>Sum Bids: {sum_bids} {f'x{more_bids}' if more_bids > more_asks else ''}</b>"
            + f"\n Current date: {order_book.update_date('current')}"
            + f"\n Update date: {order_book.update_date('update')}"
        )
