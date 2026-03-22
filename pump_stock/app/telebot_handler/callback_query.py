# -*- coding: utf-8 -*-
import json
import asyncio
import gate_api.exceptions

from functools import wraps
from prettytable import PrettyTable

import algorithm
from . import alias, literals as lit
import util
from database import model
from gate_wrapper import spot
from config import (
    bot,
    TELEGRAM_BOT,
    CONTAINER_ID,
    api_client,
    sql_req,
)


__all__ = [
    "update_currency",
    "more_info",
    "cancel_all_order",
    "list_order",
    "certain_list_my_notes",
    "uniq_text_in_notes",
    "list_uniq_text_in_notes",
    "clear_note",
    "note",
]


def access_only_creator(func):
    @wraps(func)
    async def wrapper(call):
        if (
            TELEGRAM_BOT.get("chat_id") == call.message.chat.id
            or CONTAINER_ID == call.message.chat.id
        ):
            return await func(call)

    return wrapper


@bot.callback_query_handler(
    func=lambda call: call.data
    and json.loads(call.data).get(alias.ACTION) == alias.UNIQ_TEXT_IN_NOTES
)
@access_only_creator
async def uniq_text_in_notes(call) -> None:

    payload = dict()
    payload["list of texts"] = {
        alias.ACTION: alias.LIST_UNIQ_TEXT_IN_NOTES,
    }
    buttons = util.TelegramButtons(payload)
    await bot.edit_message_text(
        f"Unique text in notes",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=buttons.create_inline_keyboard(row_width=1),
    )


def formation_uniq_text(notes) -> list[str]:

    uniq_text = sorted(set(note[0].text for note in notes))
    mount = {text: set() for text in uniq_text}
    for note in notes:
        mount[note[0].text].add(note[0].currency)
    mount = {key: sorted(data) for key, data in mount.items()}
    return [f"\"{key}\": <b>{', '.join(data)}</b>" for key, data in mount.items()]


@bot.callback_query_handler(
    func=lambda call: call.data
    and json.loads(call.data).get(alias.ACTION) == alias.LIST_UNIQ_TEXT_IN_NOTES
)
@access_only_creator
async def list_uniq_text_in_notes(call) -> None:

    req = sql_req.new_session(expire_on_commit=False)
    notes = await req.find_all_by(model.Note, t_user_id=call.from_user.id)
    payload = dict()
    payload["<< Back"] = {
        alias.ACTION: alias.UNIQ_TEXT_IN_NOTES,
    }
    buttons = util.TelegramButtons(payload)
    await bot.edit_message_text(
        f"Unique text in notes:\n\n"
        + f"{lit.TAB}{f'{lit._N}{lit.TAB}'.join(formation_uniq_text(notes))}",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=buttons.create_inline_keyboard(row_width=2),
        parse_mode="HTML",
    )


@bot.callback_query_handler(
    func=lambda call: call.data
    and json.loads(call.data).get(alias.ACTION) == alias.CLEAR_NOTE
)
@access_only_creator
async def clear_note(call) -> None:

    id = json.loads(call.data).get(alias.ID)
    req = sql_req.new_session(expire_on_commit=False)
    await req.delete_by(model.Note, id)
    await note(call)


@bot.callback_query_handler(
    func=lambda call: call.data
    and json.loads(call.data).get(alias.ACTION) == alias.NOTE
)
@access_only_creator
async def note(call) -> None:

    currency = json.loads(call.data).get(alias.CURRENT)
    req = sql_req.new_session(expire_on_commit=False)
    note = await req.find_by(model.Note, currency=currency)
    back = json.loads(call.data).get(alias.BACK)
    type_algorithm = json.loads(call.data).get(alias.ALGORITHM)
    payload = dict()
    if type_algorithm:
        payload["<< Back"] = {
            alias.ACTION: alias.UPDATE_CURRENT,
            alias.ALGORITHM: type_algorithm,
            alias.CURRENT: currency,
        }
    elif back:
        payload["<< Back"] = {
            alias.ACTION: back,
            alias.CURRENT: currency,
        }
    if note and not type_algorithm:
        payload["Clear"] = {
            alias.ACTION: alias.CLEAR_NOTE,
            alias.BACK: back,
            alias.CURRENT: currency,
            alias.ID: note[0].id,
        }
    buttons = util.TelegramButtons(payload)
    text = (
        f'<b>Note of <a href="https://www.gate.io/ru/trade/{currency}_USDT">{currency}</a> :</b>\n\n'
        + (f"{note[0].text}\n\n" if note else "")
        + (
            f"<b>Date creation:</b> {util.SumOrderbook.s_update_date(note[0].unix_time)}"
            if note
            else ""
        )
    )
    await bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=buttons.create_inline_keyboard(row_width=2),
        parse_mode="HTML",
    )


@bot.callback_query_handler(
    func=lambda call: call.data
    and json.loads(call.data).get(alias.ACTION) == alias.UPDATE_CURRENT
)
@access_only_creator
async def update_currency(call) -> None:

    try:
        currency = json.loads(call.data).get(alias.CURRENT)
        type_algorithm = json.loads(call.data).get(alias.ALGORITHM)
        functor = algorithm.concrete_functor_by(type_algorithm)
        functor.gate_req = spot.Spot(api_client)
        functor.sql_req = sql_req.new_session(expire_on_commit=False)
        functor.cont_filter = util.ContentFilter(
            [lambda x: (x.quote == "USDT" and x.base == currency)]
        )
        task = asyncio.create_task(functor())
        await task
        for data in task.result().result:
            await bot.edit_message_text(
                data.info,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=data.keyboard,
                parse_mode="HTML",
            )
    except gate_api.exceptions.ApiValueError as err:
        await bot.send_message(
            call.message.chat.id,
            f"<b>ERROR:</b> {err}",
            disable_notification=True,
        )


@bot.callback_query_handler(
    func=lambda call: call.data
    and json.loads(call.data).get(alias.ACTION) == alias.CERTAIN_LIST_MY_NOTES
)
@access_only_creator
async def certain_list_my_notes(call) -> None:

    currency = json.loads(call.data).get(alias.CURRENT)
    req = sql_req.new_session(expire_on_commit=False)
    notes = await req.find_all_by(model.Note, t_user_id=call.from_user.id)
    if notes:
        i = 0
        while notes:
            payload = dict()
            for note in notes[:50]:
                payload[note[0].currency] = {
                    alias.ACTION: alias.NOTE,
                    alias.CURRENT: note[0].currency,
                    alias.ID: note[0].id,
                    alias.BACK: alias.CERTAIN_LIST_MY_NOTES,
                }
            if currency in payload:
                buttons = util.TelegramButtons(payload)
                await bot.edit_message_text(
                    f"The list №{i} my notes:",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=buttons.create_inline_keyboard(row_width=6),
                )
                break
            else:
                del notes[:50]
                i += 1
    else:
        await bot.reply_to(
            call.message,
            "The list of notes is empty!",
            # disable_notification=True,
        )


@bot.callback_query_handler(
    func=lambda call: call.data
    and json.loads(call.data).get(alias.ACTION) == alias.LIST_ORDER
)
@access_only_creator
async def list_order(call) -> None:

    currency = json.loads(call.data).get(alias.CURRENT)
    type_algorithm = json.loads(call.data).get(alias.ALGORITHM)
    back = json.loads(call.data).get(alias.BACK)
    gate_req = spot.Spot(api_client)
    try:
        orders = await gate_req.list_orders(
            async_req=True, currency_pair=f"{currency}_USDT", status="open"
        )
    except gate_api.exceptions.ApiValueError as err:
        await bot.send_message(
            call.message.chat.id,
            f"<b>ERROR:</b> {err}",
            disable_notification=True,
        )
    buttons = util.TelegramButtons(
        {
            "<< Back": {
                alias.ACTION: back,
                alias.ALGORITHM: type_algorithm,
                alias.CURRENT: currency,
            },
            "Cancel all open orders": {
                alias.ACTION: alias.CANCEL_ALL_ORDERS,
                alias.BACK: back,
                alias.CURRENT: currency,
            },
        }
    )
    tables = str()
    for data in orders:
        data.create_time = util.SumOrderbook.s_update_date(data.create_time)
        data.update_time = util.SumOrderbook.s_update_date(data.update_time)
        table = util.Table(
            data.dict(), pretty=PrettyTable(header=False, max_table_width=45)
        ).get_string(total_items_row=3)
        tables += f"{table}\n"
    await bot.edit_message_text(
        f'<b>List of <a href="https://www.gate.io/ru/trade/{currency}_USDT">{currency}</a> orders</b>{tables}'
        + '<a href="https://www.gate.io/docs/developers/apiv4/en/#list-orders">API information</a>',
        call.message.chat.id,
        call.message.message_id,
        reply_markup=buttons.create_inline_keyboard(row_width=2),
        parse_mode="HTML",
        # disable_notification=True,
    )


@bot.callback_query_handler(
    func=lambda call: call.data
    and json.loads(call.data).get(alias.ACTION) == alias.CANCEL_ALL_ORDERS
)
@access_only_creator
async def cancel_all_order(call) -> None:

    currency = json.loads(call.data).get(alias.CURRENT)
    gate_req = spot.Spot(api_client)
    try:
        await gate_req.cancel_orders(async_req=True, currency_pair=f"{currency}_USDT")
    except gate_api.exceptions.ApiValueError as err:
        await bot.send_message(
            call.message.chat.id,
            f"<b>ERROR:</b> {err}",
            disable_notification=True,
        )
    await list_order(call)


@bot.callback_query_handler(
    func=lambda call: call.data
    and json.loads(call.data).get(alias.ACTION) == alias.MORE_INFO
)
@access_only_creator
async def more_info(call) -> None:

    currency = json.loads(call.data).get(alias.CURRENT)
    type_algorithm = json.loads(call.data).get(alias.ALGORITHM)
    back = json.loads(call.data).get(alias.BACK)
    gate_req = spot.Spot(api_client)
    try:
        tickers = await gate_req.list_tickers(
            async_req=True, currency_pair=f"{currency}_USDT"
        )
    except gate_api.exceptions.ApiValueError as err:
        await bot.send_message(
            call.message.chat.id,
            f"<b>ERROR:</b> {err}",
            disable_notification=True,
        )
    buttons = util.TelegramButtons(
        {
            "<< Back": {
                alias.ACTION: back,
                alias.ALGORITHM: type_algorithm,
                alias.CURRENT: currency,
            }
        }
    )
    table = util.Table(
        tickers[0].dict(), pretty=PrettyTable(header=False, max_table_width=45)
    ).get_string(total_items_row=4)
    await bot.edit_message_text(
        f'<b>More information about <a href="https://www.gate.io/ru/trade/{currency}_USDT">{currency}</a></b>{table}\n'
        + '<a href="https://www.gate.io/docs/developers/apiv4/en/#retrieve-ticker-information">API information</a>',
        call.message.chat.id,
        call.message.message_id,
        reply_markup=buttons.create_inline_keyboard(row_width=2),
        parse_mode="HTML",
        # disable_notification=True,
    )
