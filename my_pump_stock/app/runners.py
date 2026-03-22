# -*- coding: utf-8 -*-
"""Данная программа ищет все активы, котрые находятся на текущий момент в портфеле пользователя и
формирует отчет по текущим алгаритмам которые реализованы в algorithm.py"""
import asyncio
import logging
import gate_api.exceptions

from telebot import asyncio_helper

import global_obj
import algorithm
import util

from gate_wrapper import parse
from database import model
from config import bot, TELEGRAM_BOT, sql_req, GATE_API_DOMAIN


__all__ = ["action", "auto_action"]


async def auto_action(*args, **kwargs):

    try:
        if not (global_obj.PAUSE or global_obj.MANUAL):
            if global_obj.AUTO:
                return
            global_obj.AUTO = True
            await action(*args, **kwargs)
    finally:
        global_obj.AUTO = False


async def save_arith_mean(alg: algorithm.AsyncAlgorithm):

    req = sql_req.new_session(expire_on_commit=False)
    arith_mean = await req.find_by(
        model.ArithmeticMean,
        bot_name=alg.config.bot_name,
        algorithm_id=alg.config.id,
    )
    total_seconds = alg.delta_time.total_seconds()
    await req.upsert_by(
        model.ArithmeticMean,
        filter_by={
            "bot_name": alg.config.bot_name,
            "t_user_id": TELEGRAM_BOT["chat_id"],
            "algorithm_id": alg.config.id,
        },
        values={
            "times": arith_mean[0].times + 1 if arith_mean else 1,
            "seconds": (
                arith_mean[0].seconds + total_seconds if arith_mean else total_seconds
            ),
        },
    )


async def save_more_info(alg: algorithm.AsyncAlgorithm, currencys):

    req = sql_req.new_session(expire_on_commit=False)
    for cur in currencys:
        try:
            tickers = await algorithm.AsyncAlgorithm.gate_req(
                f"http://{GATE_API_DOMAIN}/spot/tickers?currency_pair={cur}_USDT"
            )
            tickers = parse.ParseTickers(tickers).parse()
            await req.add_by(
                model.AllPumpStocks,
                t_user_id=TELEGRAM_BOT["chat_id"],
                algorithm_id=alg.config.id,
                bot_name=alg.config.bot_name,
                **tickers[0].dict(),
            )
        except gate_api.exceptions.ApiValueError as err:
            await bot.send_message(
                TELEGRAM_BOT["chat_id"],
                f"<b>ERROR:</b> {err}",
                disable_notification=True,
            )


async def send_results(alg: algorithm.AsyncAlgorithm) -> None:

    try:
        currencys = list()
        for data in alg.result:
            currencys.append(data.currency)
            await bot.send_message(
                TELEGRAM_BOT["chat_id"],
                data.info,
                # disable_notification=True,
                parse_mode="HTML",
                reply_markup=data.keyboard,
            )
            await asyncio.sleep(0.3)
    except asyncio_helper.ApiTelegramException as err:
        if (
            "Too Many Requests: retry after" in err.description
            and err.error_code == 429
        ):
            logging.error(f"Caught a Telegram API Exception: {err}")
            seconds = int(err.description.split(" ")[-1])
            # await bot.send_message(
            #     TELEGRAM_BOT["chat_id"],
            #     f"I'm wating for {seconds} due to: {err}",
            #     # disable_notification=True,
            #     parse_mode="HTML",
            #     reply_markup=data.get("keyboard"),
            # )
            await asyncio.sleep(seconds)
            await send_results(alg)
    finally:
        await save_arith_mean(alg)
        await save_more_info(alg, currencys)


async def action(type_algorithm="1") -> None:

    try:
        alg = algorithm.concrete_functor_by(type_algorithm)
        alg.cont_filter = util.ContentFilter(
            [
                lambda d: (
                    float(d.available) > 0.1
                    and "USDT" not in d.currency
                    and d.currency not in global_obj.EXCLUDED_SPOTS
                )
            ]
        )
        alg.sql_req = sql_req.new_session(expire_on_commit=False)
        if global_obj.MANUAL:
            info = await alg.config.info(
                with_title=True, manual=True if global_obj.MANUAL else False
            )
            await bot.send_message(
                TELEGRAM_BOT["chat_id"],
                info,
                disable_notification=True,
                parse_mode="HTML",
            )
        await alg()
        await send_results(alg)
    except (gate_api.exceptions.ApiValueError, Exception) as err:
        await bot.send_message(
            TELEGRAM_BOT["chat_id"],
            f'<b>ERROR:</b> {err if err.__str__() else "There is an internal error!"}',
            disable_notification=True,
            parse_mode="HTML",
        )
        raise
