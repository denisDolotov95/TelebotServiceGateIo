# -*- coding: utf-8 -*-
import telebot
import re

from functools import wraps

import util
import global_obj
import runners as run
import literals as lit

from config import (
    bot,
    TELEGRAM_BOT,
    INFO_COMMANDS,
    LOG_FILE_NAME,
    CONTAINER_ID,
    GATE_API_DOMAIN,
)

from gate_wrapper import parse


def access_only_creator(func):
    """Политики доступа к обработчикам

    Args:
        func (_type_): _description_

    Returns:
        _type_: _description_
    """

    @wraps(func)
    async def wrapper(message):
        if (
            int(TELEGRAM_BOT.get("chat_id")) == int(message.chat.id)
            or CONTAINER_ID == message.chat.id
        ):
            return await func(message)

    return wrapper


@bot.message_handler(commands="balance")
@access_only_creator
async def handle_commands_message(message):
    """Обработка комманды balance

    Args:
        message (_type_): объект сообщения из telebot
    """
    total_balance = await util.gate_req(
        f"http://{GATE_API_DOMAIN}/wallet/total_balance"
    )
    total_balance = parse.ParseTotalBalance(total_balance).parse()
    total, details = util.formation_total_balance_table(total_balance)
    await bot.reply_to(
        message,
        f"<pre>{total}\n\n{details}</pre>",
        parse_mode="HTML",
        # disable_notification=True,
    )


@bot.message_handler(commands="logs")
@access_only_creator
async def command_logs(message):
    """Обработка комманды logs

    Args:
        message (_type_): объект сообщения из telebot
    """
    with open(f"./log/{LOG_FILE_NAME}.log", "rb") as f:
        await bot.send_document(
            message.chat.id,
            f.read(),
            visible_file_name=f"{LOG_FILE_NAME.split('_', 1)[1]}.log",
        )


@bot.message_handler(
    func=lambda message: bool(
        re.fullmatch(
            r"P2P\ (покупка|продажа)\ [A-Z]{1,10}-[A-Z]{1,10}",
            message.text,
        )
    ),
    content_types=["text"],
)
@access_only_creator
async def command_check_p2p(message):
    """Обработка текстового запроса на получение текущих P2P сделок

    Args:
        message (_type_): объект сообщения из telebot
    """
    text = message.text.split(" ")
    _type = {
        lit.P2P_BUY_USDT: f"/buy/{text[-1]}",
        lit.P2P_SELL_USDT: f"/sell/{text[-1]}",
    }

    await run.check_p2p(url=lit.URL_PATH_P2P, _type=_type[f"{text[0]} {text[1]}"])


@bot.message_handler(commands="check_delisted_info")
@access_only_creator
async def command_check_delisted_info(message):
    """Обработка комманды check_delisted_info

    Args:
        message (_type_): объект сообщения из telebot
    """
    await run.action_2(url=lit.URL_PATH_ANNONCE)


@bot.message_handler(commands="add_buttons")
@access_only_creator
async def handle_add_buttons(message):
    """Добавление кнопок на главную панель в приложении

    Args:
        message (_type_): объект сообщения из telebot
    """
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    callback_button_help = telebot.types.KeyboardButton("/help")
    # callback_check = telebot.types.KeyboardButton("/check")
    # callback_active = telebot.types.KeyboardButton("/active")
    # callback_pause = telebot.types.KeyboardButton("/pause")
    callback_button_balance = telebot.types.KeyboardButton("/balance")
    callback_buy = telebot.types.KeyboardButton(f"{lit.P2P_BUY_USDT} RUB-USDT")
    callback_sell = telebot.types.KeyboardButton(f"{lit.P2P_SELL_USDT} USDT-RUB")
    markup.add(
        callback_button_help,
        # callback_check,
        # callback_active,
        # callback_pause,
        callback_button_balance,
        callback_buy,
        callback_sell,
    )
    await bot.reply_to(
        message,
        "Keyboard has been added.",
        reply_markup=markup,
        # disable_notification=True,
    )


@bot.message_handler(commands="check")
@access_only_creator
async def handle_check(message):
    """Проверка состояния бота

    Args:
        message (_type_): объект сообщения из telebot
    """

    if not global_obj.PAUSE:
        await bot.reply_to(
            message,
            "I'm active!",
            # disable_notification=True,
        )
    else:
        await bot.reply_to(
            message,
            "I'm on pause!",
            # disable_notification=True,
        )


@bot.message_handler(commands="pause")
@access_only_creator
async def handle_pause(message):
    """Поставить бота на паузу

    Args:
        message (_type_): объект сообщения из telebot
    """
    global_obj.PAUSE = True
    await bot.reply_to(
        message,
        "I'm on pause!",
        # disable_notification=True,
    )


@bot.message_handler(commands="active")
@access_only_creator
async def handle_active(message):
    """Активировать бота

    Args:
        message (_type_): объект сообщения из telebot
    """
    global_obj.PAUSE = False
    await bot.reply_to(
        message,
        "Started working!",
        # disable_notification=True,
    )


@bot.message_handler(commands="stop")
@access_only_creator
async def handle_stop(message):
    """Послать комманду боту, чтобы завершить процесс (скрипта).
    Если данный экземпляр поднят в докер контейнере с флагом "restart: always",
    то бот запустится с иходным состоянием.

    Args:
        message (_type_): объект сообщения из telebot
    """
    await bot.reply_to(
        message,
        f"The bot stops working!",
        parse_mode="HTML",
        # disable_notification=True
    )
    import os

    os._exit(os.EX_OK)


@bot.message_handler(commands="help")
@access_only_creator
async def handle_help(message):
    """Информация по всем команам бота

    Args:
        message (_type_): объект сообщения из telebot
    """
    await bot.reply_to(
        message,
        util.formation_info_by_commands(INFO_COMMANDS),
        parse_mode="HTML",
        # disable_notification=True
    )


@bot.message_handler(commands="del_buttons")
@access_only_creator
async def handle_del_buttons(message):
    """Удалить все кнопки из главной панели приложения

    Args:
        message (_type_): объект сообщения из telebot
    """
    await bot.reply_to(
        message,
        "Keyboard has been deleted.",
        reply_markup=telebot.types.ReplyKeyboardRemove(selective=False),
        # disable_notification=True,
    )


@bot.message_handler(func=lambda message: message.text)
@access_only_creator
async def message_text(message) -> None:
    """Обработка всех возможных текстовых сообщений

    Args:
        message (_type_): объект сообщения из telebot
    """
    await bot.reply_to(
        message,
        "The command didn't found!",
        parse_mode="HTML",
        # disable_notification=True,
    )
