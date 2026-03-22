# -*- coding: utf-8 -*-
import os
import re
import asyncio
import telebot
import gate_api.exceptions

from functools import wraps

import global_obj
import runners
import util

from . import alias
from database import model
from gate_wrapper import spot
from config import (
    bot,
    TELEGRAM_BOT,
    CONTAINER_ID,
    LOG_FILE_NAME,
    api_client,
    sql_req,
    Config,
    ConfAlgorithm1,
    ConfAlgorithm2,
    ConfAlgorithm3,
    ConfAlgorithm4,
    ConfAlgorithm5,
    Commands,
    Text,
    HTML,
    Pdf,
    MessegeFlow,
)

__all__ = [
    "command_add_buttons",
    "command_add_note",
    "command_algorithm",
    "command_list_my_notes",
    "command_picture",
    "command_logs",
    "command_readme",
    "commands_message",
    "message_edit_interval",
    "message_edit_limit",
    "message_edit_order_book_limit",
    "message_edit_order_book_ratio",
    "message_edit_percent",
    "message_edit_price",
    "message_edit_ratio_4",
    "message_edit_split",
    "message_text",
]


def access_only_creator(func):
    @wraps(func)
    async def wrapper(message):
        if (
            TELEGRAM_BOT.get("chat_id") == message.chat.id
            or CONTAINER_ID == message.chat.id
        ):
            return await func(message)

    return wrapper


@bot.message_handler(commands="list_my_notes")
@access_only_creator
async def command_list_my_notes(message) -> None:

    req = sql_req.new_session(expire_on_commit=False)
    notes = await req.find_all_by(model.Note, t_user_id=message.from_user.id)
    if notes:
        payload = dict()
        payload["list of texts"] = {
            alias.ACTION: alias.LIST_UNIQ_TEXT_IN_NOTES,
        }
        buttons = util.TelegramButtons(payload)
        await bot.send_message(
            message.chat.id,
            f"Unique text in notes",
            reply_markup=buttons.create_inline_keyboard(row_width=1),
            disable_notification=True,
        )
        i = 0
        notes = sorted(notes, key=lambda note: note[0].currency)
        while notes:
            payload.clear()
            for note in notes[:50]:
                payload[note[0].currency] = {
                    alias.ACTION: alias.NOTE,
                    alias.CURRENT: note[0].currency,
                    alias.ID: note[0].id,
                    alias.BACK: alias.CERTAIN_LIST_MY_NOTES,
                }
            buttons = util.TelegramButtons(payload)
            await bot.send_message(
                message.chat.id,
                f"The list №{i} my notes:",
                reply_markup=buttons.create_inline_keyboard(row_width=6),
                disable_notification=True,
            )
            del notes[:50]
            i += 1
    else:
        await bot.reply_to(
            message,
            "The list of notes is empty!",
            # disable_notification=True,
        )


@bot.message_handler(
    func=lambda message: bool(re.fullmatch(r"/note \w+ .+", message.text))
)
@access_only_creator
async def command_add_note(message) -> None:

    _, currency, text = message.text.split(" ", 2)
    if len(text) > 1024:
        await bot.reply_to(message, f"The length of the text > 1024!")
    gate_req = spot.Spot(api_client)
    try:
        pairs = await gate_req.list_currency_pairs(async_req=True)
    except gate_api.exceptions.ApiValueError as err:
        await bot.send_message(
            message.chat.id,
            f"<b>ERROR:</b> {err}",
            disable_notification=True,
            parse_mode="HTML",
        )
    filter = util.ContentFilter([lambda d: d.base == currency])
    if filter.filter(pairs):
        req = sql_req.new_session(expire_on_commit=False)
        await req.upsert_by(
            model.Note,
            filter_by={"currency": currency, "t_user_id": message.from_user.id},
            values={"text": text},
        )
        await bot.reply_to(
            message,
            "The note has been added.",
            # disable_notification=True,
        )
    else:
        await bot.reply_to(
            message,
            "This currency does not exist!",
            # disable_notification=True,
        )


@bot.message_handler(commands="add_buttons")
@access_only_creator
async def command_add_buttons(message) -> None:

    buttons = util.TelegramButtons(
        ["/help", "/check", "/active", "/pause", "/current_conf"]
    )
    await bot.reply_to(
        message,
        "Keyboard has been added.",
        reply_markup=buttons.create_reply_keyboard(
            resize_keyboard=True,
        ),
        # disable_notification=True,
    )


@bot.message_handler(
    func=lambda message: bool(re.fullmatch(r"/algorithm_(1|2|3|4|5)", message.text))
)
@access_only_creator
async def command_algorithm(message) -> None:

    if global_obj.PAUSE:
        await bot.reply_to(
            message,
            "I'm on pause!",
            # parse_mode="HTML",
            # disable_notification=True
        )
        return
    if global_obj.MANUAL:
        await bot.reply_to(
            message,
            "The manual execution has already been activated!",
            # parse_mode="HTML",
            # disable_notification=True
        )
        return
    try:
        global_obj.MANUAL = True
        await bot.reply_to(
            message,
            "The manual execution has started!",
            # parse_mode="HTML",
            # disable_notification=True
        )
        type_algorithm = message.text.split("_")[1]
        task = asyncio.create_task(runners.action(type_algorithm))
        await task
        await bot.reply_to(
            message,
            "The manual execution has completed!",
            # parse_mode="HTML",
            # disable_notification=True
        )
    finally:
        global_obj.MANUAL = False


@bot.message_handler(commands="readme")
@access_only_creator
async def command_readme(message) -> None:

    with open("data/img/README.png", "rb") as f:
        await bot.send_photo(
            message.chat.id,
            f.read(),
        )

@bot.message_handler(commands="logs")
@access_only_creator
async def command_logs(message) -> None:

    with open(f"./log/{LOG_FILE_NAME}.log", "rb") as f:
        await bot.send_document(
            message.chat.id,
            f.read(),
            visible_file_name=f"{LOG_FILE_NAME.split('_', 1)[1]}.log"
        )


@bot.message_handler(
    func=lambda message: bool(re.fullmatch(r"/picture_(1|2|3|4|5)", message.text))
)
@access_only_creator
async def command_picture(message) -> None:

    pic = dict()
    for conf in (ConfAlgorithm1, ConfAlgorithm2, ConfAlgorithm3, ConfAlgorithm4):
        pic[conf.id] = conf.path_picture
    try:
        id = int(message.text.split("_")[1])
        with open(pic[id], "rb") as f:
            byte = f.read()
        await bot.send_photo(
            message.chat.id,
            byte,
        )
    except FileNotFoundError as err:
        await bot.send_message(
            message.chat.id,
            f"<b>ERROR:</b> {err}",
            disable_notification=True,
            parse_mode="HTML",
        )


@bot.message_handler(
    commands={
        "check",
        "add_buttons",
        "del_buttons",
        "help",
        "stop",
        "pause",
        "active",
        "current_conf",
        "version",
        "version_py",
    }
)
@access_only_creator
async def commands_message(message) -> None:

    if message.text == "/check":
        if not global_obj.PAUSE:
            text = (
                "I was activated automatically (planned tasks)!"
                if global_obj.AUTO
                else (
                    "I was activated manually!"
                    if global_obj.MANUAL
                    else "I'm waiting..."
                )
            )
            await bot.reply_to(
                message,
                text,
                # disable_notification=True,
            )
        else:
            await bot.reply_to(
                message,
                "I'm on pause!",
                # disable_notification=True,
            )
    elif message.text == "/pause":
        global_obj.PAUSE = True
        await bot.reply_to(
            message,
            "I'm on pause!",
            # disable_notification=True,
        )
    elif message.text == "/active":
        if not (global_obj.AUTO or global_obj.MANUAL) or global_obj.PAUSE:
            global_obj.PAUSE = False
            await bot.reply_to(
                message,
                "Started working!",
                # disable_notification=True,
            )
        else:
            await bot.reply_to(
                message,
                "i'm already working!",
                # disable_notification=True,
            )
    elif message.text == "/stop":
        await bot.reply_to(
            message,
            f"The bot stops working!",
            parse_mode="HTML",
            # disable_notification=True
        )
        os._exit(os.EX_OK)
    elif message.text == "/help":
        await bot.reply_to(
            message,
            Commands.to_text(),
            parse_mode="HTML",
            # disable_notification=True
        )
    elif message.text == "/version":
        await bot.reply_to(
            message,
            os.getenv("VERSION"),
            # disable_notification=True
        )
    elif message.text == "/version_py":
        await bot.reply_to(
            message,
            os.getenv("PYTHON_VERSION"),
            # disable_notification=True
        )
    elif message.text == "/current_conf":
        text = ""
        for conf in (
            ConfAlgorithm1,
            ConfAlgorithm2,
            ConfAlgorithm3,
            ConfAlgorithm4,
            ConfAlgorithm5,
        ):
            text += await conf.info(
                with_action=True, with_picture=True, with_commands=True
            )
            text += "\n"
        await bot.reply_to(
            message,
            text,
            parse_mode="HTML",
            # disable_notification=True
        )
    elif message.text == "/del_buttons":
        markup = telebot.types.ReplyKeyboardRemove(selective=False)
        await bot.reply_to(
            message,
            "Keyboard has been deleted.",
            reply_markup=markup,
            # disable_notification=True,
        )


@bot.message_handler(
    func=lambda message: bool(re.fullmatch(r"/edit_ratio_4 \d+", message.text))
)
@access_only_creator
async def message_edit_ratio_4(message) -> None:

    ConfAlgorithm4.trade_ratio = int(message.text.split(" ")[1])
    info = await ConfAlgorithm4.info()
    await bot.reply_to(
        message,
        f"The ratio has been edited to <b>{ConfAlgorithm4.trade_ratio}</b>\n"
        + f"{info}",
        parse_mode="HTML",
    )


@bot.message_handler(
    func=lambda message: bool(re.fullmatch(r"/edit_price \d+", message.text))
)
@access_only_creator
async def message_edit_price(message) -> None:

    ConfAlgorithm2.price_ratio = int(message.text.split(" ")[1])
    info = await ConfAlgorithm2.info()
    await bot.reply_to(
        message,
        f"The price has been edited to <b>{ConfAlgorithm2.price_ratio}</b>\n"
        + f"{info}",
        parse_mode="HTML",
    )


@bot.message_handler(
    func=lambda message: bool(re.fullmatch(r"/edit_split \d+", message.text))
)
@access_only_creator
async def message_edit_split(message) -> None:

    split = int(message.text.split(" ")[1])
    if split > ConfAlgorithm5.bar_limit:
        await bot.reply_to(
            message,
            f"The split more than {ConfAlgorithm5.bar_limit}!",
            parse_mode="HTML",
        )
        return
    ConfAlgorithm5.split = int(message.text.split(" ")[1])
    info = await ConfAlgorithm5.info()
    await bot.reply_to(
        message,
        f"The split has been edited to <b>{ConfAlgorithm5.split}</b>\n" + f"{info}",
        parse_mode="HTML",
    )


@bot.message_handler(
    func=lambda message: bool(
        re.fullmatch(
            f"/edit_candle_price ({'|'.join(ConfAlgorithm5.alias_candle_price.keys())})",
            message.text,
        )
    )
)
@access_only_creator
async def message_candle_price(message) -> None:
    
    ConfAlgorithm5.candle_price = str(message.text.split(" ")[1])
    info = await ConfAlgorithm5.info()
    await bot.reply_to(
        message,
        f"The candle price has been edited to <b>{ConfAlgorithm5.candle_price}</b>\n"
        + f"{info}",
        parse_mode="HTML",
    )


@bot.message_handler(
    func=lambda message: bool(re.fullmatch(r"/edit_order_book_ratio \d+", message.text))
)
@access_only_creator
async def message_edit_order_book_ratio(message) -> None:

    ConfAlgorithm3.order_book_ratio = int(message.text.split(" ")[1])
    info = await ConfAlgorithm3.info()
    await bot.reply_to(
        message,
        f"The order book ratio has been edited to <b>{ConfAlgorithm3.order_book_ratio}</b>\n"
        + f"{info}",
        parse_mode="HTML",
    )


@bot.message_handler(
    func=lambda message: bool(re.fullmatch(r"/edit_order_book_limit \d+", message.text))
)
@access_only_creator
async def message_edit_order_book_limit(message) -> None:

    Config.order_book_limit = int(message.text.split(" ")[1])
    await bot.reply_to(
        message,
        f"The order book limit has been edited to <b>{Config.order_book_limit}</b>",
        parse_mode="HTML",
    )


@bot.message_handler(
    func=lambda message: bool(re.fullmatch(r"/edit_limit_\d+ \d+", message.text))
)
@access_only_creator
async def message_edit_limit(message) -> None:

    id = int(message.text.split(" ")[0].split("_")[-1])
    for conf in (
        ConfAlgorithm1,
        ConfAlgorithm2,
        ConfAlgorithm3,
        ConfAlgorithm4,
        ConfAlgorithm5,
    ):
        if conf.id == id:
            conf.bar_limit = int(message.text.split(" ")[1])
            if conf == ConfAlgorithm5 and conf.bar_limit < conf.split:
                conf.split = conf.bar_limit
            info = await conf.info()
            await bot.reply_to(
                message,
                f"The limit has been edited to <b>{conf.bar_limit}</b>\n" + f"{info}",
                parse_mode="HTML",
            )
            break


@bot.message_handler(
    func=lambda message: bool(
        re.fullmatch(r"/edit_percent_\d+ (-?\d+(\.\d+)?)", message.text)
    )
)
@access_only_creator
async def message_edit_percent(message) -> None:

    id = int(message.text.split(" ")[0].split("_")[-1])
    for conf in (ConfAlgorithm1, ConfAlgorithm2, ConfAlgorithm3, ConfAlgorithm5):
        if conf.id == id:
            conf.percent = float(message.text.split(" ")[1])
            info = await conf.info()
            await bot.reply_to(
                message,
                f"The percent has been edited to <b>{conf.percent}</b>\n" + f"{info}",
                parse_mode="HTML",
            )
            break


@bot.message_handler(
        func=lambda message: bool(
            re.fullmatch(r"/drop_time_\d+", message.text)
        )
)
@access_only_creator
async def message_drop_time(message):

    id = int(message.text.split(" ")[0].split("_")[-1])
    for conf in (
        ConfAlgorithm1,
        ConfAlgorithm2,
        ConfAlgorithm3,
        ConfAlgorithm4,
        ConfAlgorithm5,
    ):
        if conf.id == id:
            req = sql_req.new_session(expire_on_commit=False)
            await req.update_by(model.ArithmeticMean,
                                filter_by={"algorithm_id": conf.id, "t_user_id": message.from_user.id},
                                values={"seconds": 0.0, 'times': 0})
            info = await conf.info()
            await bot.reply_to(
                message,
                f"The average time has been dropped\n"
                + f"{info}",
                parse_mode="HTML",
            )
            break    

@bot.message_handler(
    func=lambda message: bool(
        re.fullmatch(
            r"/edit_interval_\d+ (10s|1m|5m|15m|30m|1h|4h|8h|1d|7d|30d)",
            message.text,
        )
    )
)
@access_only_creator
async def message_edit_interval(message) -> None:

    id = int(message.text.split(" ")[0].split("_")[-1])
    for conf in (
        ConfAlgorithm1,
        ConfAlgorithm2,
        ConfAlgorithm3,
        ConfAlgorithm4,
        ConfAlgorithm5,
    ):
        if conf.id == id:
            conf.bar_interval = message.text.split(" ")[1]
            info = await conf.info()
            await bot.reply_to(
                message,
                f"The interval has been edited to <b>{conf.bar_interval}</b>\n"
                + f"{info}",
                parse_mode="HTML",
            )
            break


@bot.message_handler(
    func=lambda message: bool(
        re.fullmatch(
            f"/edit_type_output ({Text.type}|{HTML.type}|{Pdf.type}|{MessegeFlow.type})",
            message.text,
        )
    )
)
@access_only_creator
async def message_type_output(message) -> None:

    type = str(message.text.split(" ")[1])
    for conf in (
        ConfAlgorithm1,
        ConfAlgorithm2,
        ConfAlgorithm3,
        ConfAlgorithm4,
        ConfAlgorithm5,
    ):
        conf.output.type = type
        conf.output.is_file = True
        info = await conf.info()
        await bot.reply_to(
            message,
            f"The type output has been edited to <b>{conf.output.type}</b>\n"
            + f"{info}",
            parse_mode="HTML",
        )
        # break


@bot.message_handler(func=lambda message: message.text)
@access_only_creator
async def message_text(message) -> None:

    await bot.reply_to(
        message,
        "The command didn't found!",
        parse_mode="HTML",
        # disable_notification=True,
    )
