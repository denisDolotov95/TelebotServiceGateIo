# -*- coding: utf-8 -*-
import asyncio
import logging
import traceback
import concurrent.futures

# import re

import global_obj
import literals as lit
import util

from functools import wraps
from gate_wrapper import parse
from config import bot, TELEGRAM_BOT, GATE_API_DOMAIN
from util import ParseGateIoHTML

__all__ = ["action", "action_2", "run_polling"]


def pause(f):

    @wraps(f)
    async def wrapper(*args, **kwargs):
        if not global_obj.PAUSE:
            await f(*args, **kwargs)

    return wrapper


@pause
async def check_p2p(
    _type: str,
    url: str = lit.URL_PATH_P2P,
):
    """Запрос в бразуер, для получения информации о текущих P2P позициях

    Args:
        _type (str): Тип P2P сделки
        url (str, optional): Путь, из которого нужно получть данные. Defaults to lit.URL_PATH_P2P.
    """
    loop = asyncio.get_running_loop()
    results = []
    with concurrent.futures.ProcessPoolExecutor(1) as pool:
        tasks = []
        tasks.append(
            loop.run_in_executor(
                pool, ParseGateIoHTML.get_page_by_selenium, f"{url}{_type}"
            )
        )
        results.append(await asyncio.gather(*tasks))

    for data in results:
        page = ParseGateIoHTML(data[0])
    text = await page.get_p2p()

    if not global_obj.CHASH.get(url):
        global_obj.CHASH[url] = text
    elif global_obj.CHASH[url] == text:
        await bot.send_message(
            TELEGRAM_BOT["chat_id"],
            f"<b><a href='{url}'>P2P orders</a></b>:\n\n<b>Nothing new!</b>",
            parse_mode="HTML",
            disable_notification=True,
        )
        return

    text: str = "\n\n".join([f"<b>{t}</b>" for t in text[:10]]) + " "

    await bot.send_message(
        TELEGRAM_BOT["chat_id"],
        f"<b><a href='{url}'>P2P</a></b>:\n\n" f"{text}",
        parse_mode="HTML",
        disable_notification=None,
    )


@pause
async def action_2(url: str = lit.URL_PATH_ANNONCE):
    """Получить информацию из браузера (анализируя/парсинг html разметку)"""

    html = await ParseGateIoHTML.get_page_by_request(url)
    if not html:
        return

    page = ParseGateIoHTML(html)
    text = await page.get_announce()

    if not global_obj.CHASH.get(url):
        global_obj.CHASH[url] = text
    elif global_obj.CHASH[url] == text:
        await bot.send_message(
            TELEGRAM_BOT["chat_id"],
            f"<b><a href='{url}'>Delisting News</a></b>:\n\n<b>Nothing new!</b>",
            parse_mode="HTML",
            disable_notification=True,
        )
        return

    text: str = "\n\n".join(text[:5]) + " "

    await bot.send_message(
        TELEGRAM_BOT["chat_id"],
        f"<b><a href='{url}'>Delisting News</a></b>:\n\n" f"{text}",
        parse_mode="HTML",
        disable_notification=None,
    )


@pause
async def action():
    """Обычная плановая задача из gate API"""
    # gate_req = wallet.Wallet(api_client)
    # total_balance = await gate_req.total_balance(async_req=True)
    total_balance = await util.gate_req(
        f"http://{GATE_API_DOMAIN}/wallet/total_balance"
    )
    total_balance = parse.ParseTotalBalance(total_balance).parse()
    total, _ = util.formation_total_balance_table(total_balance)
    await bot.send_message(
        TELEGRAM_BOT["chat_id"],
        f"<pre>{total}</pre>",
        parse_mode="HTML",
        # disable_notification=True,
    )


async def run_polling():
    """
    The `run_polling` function runs a polling loop for a bot with error handling for exceptions.
    """
    try:
        await bot.polling(none_stop=True, timeout=TELEGRAM_BOT["connect_timeout"])
    except Exception:
        logging.error(f"\n{traceback.format_exc()}\n")
