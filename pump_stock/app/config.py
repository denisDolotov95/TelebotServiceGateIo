# -*- coding: utf-8 -*-
import os
import gate_api

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from telebot import async_telebot
from database import request, engine, model
from copy import deepcopy

__all__ = [
    "ConfAlgorithm1",
    "ConfAlgorithm2",
    "ConfAlgorithm3",
    "ConfAlgorithm4",
    "ConfAlgorithm5",
    "Config",
    "DB_CONFIGURATION",
    "GATE_CONFIGURATION",
    "CONTAINER_ID",
    "BOT_NAME",
    "LOG_FILE_NAME",
    "TELEGRAM_BOT",
    "api_client",
    "bot",
    "engine",
    "sql_req",
]

CONTAINER_ID = os.environ.get("CONTAINER_ID", 0)

BOT_NAME = os.environ.get("BOT_FILE_NAME", "pump_stock")

LOG_FILE_NAME = f"{CONTAINER_ID}_{BOT_NAME}"

DB_CONFIGURATION = {
    "file_path": os.environ.get(
        "DB_FILE_PATH", os.path.join("app/database", "database.db")
    )
}

# engine = engine.EnginePSQL(**DB_CONFIGURATION)
engine = engine.EngineSQLite(**DB_CONFIGURATION)
sql_req = request._Session(engine)

LOCAL_GATE_API_IP = os.environ.get("LOCAL_GATE_REST_API_IP", "192.168.0.110")
LOCAL_GATE_API_PORT = os.environ.get("LOCAL_GATE_REST_API_PORT", "3501")
GATE_API_DOMAIN = f"{LOCAL_GATE_API_IP}:{LOCAL_GATE_API_PORT}"

GATE_CONFIGURATION = {
    "host": os.environ.get("GATE_HOST", "https://api.gateio.ws/api/v4"),
    "key": os.environ.get("GATE_KEY", "3b4a04ccc3ce615e"),
    "secret": os.environ.get(
        "GATE_SECRET",
        "13b45a963480cdc446579e8405ea6",
    ),
}

api_client = gate_api.ApiClient(gate_api.Configuration(**GATE_CONFIGURATION))

TELEGRAM_BOT = {
    "host": os.environ.get("TELEGRAM_HOST", "https://api.telegram.org"),
    "token": os.environ.get(
        "TELEGRAM_BOT_TOKEN", "6743733208:AAFA1dbd4mRYvN5b"
    ),
    "chat_id": int(os.environ.get("TELEGRAM_CHAT_ID", "58000")),
    "connect_timeout": int(os.environ.get("TELEGRAM_CONN_TIME", 60)),
}

bot = async_telebot.AsyncTeleBot(TELEGRAM_BOT["token"])


class OutputFormat:

    type: str = ""
    is_file: bool = None
    format: str = ""


class Text(OutputFormat):

    type: str = "text"
    is_file: bool = True
    format: str = "txt"


class HTML(OutputFormat):

    type: str = "html"
    is_file: bool = True
    format = "html"


class Pdf(OutputFormat):

    type: str = "pdf"
    is_file: bool = True
    format = "pdf"


class MessegeFlow(OutputFormat):

    type: str = "message"


class Config(ABC):
    """_summary_

    Args:
        ABC (_type_): _description_

    Returns:
        _type_: _description_
    """

    id = 0
    # если не получилось отправить сообщение боту в чат, то пробовать повторно
    retry_send_after_err = True
    bot_name = BOT_NAME
    output: MessegeFlow | HTML | Pdf | Text = HTML
    order_book_limit = int(os.environ.get("BOT_ORDER_BOOK_LIMIT", 30))

    @classmethod
    def action(cls, _with) -> str:

        return f"| /algorithm_{cls.id}" if _with else ""

    @classmethod
    def picture(cls, _with) -> str:

        return f"| /picture_{cls.id}" if _with else ""

    @classmethod
    def title(cls, _with) -> str:

        return (
            f'Запущен в <b>{datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")}</b> с параметрами: \n'
            if _with
            else ""
        )

    @classmethod
    def scheduler(cls, idx, manual) -> str:

        return (
            ""
            if manual
            else f"\n{idx}. Интервал между запросами <b>~ {timedelta(seconds = cls.sched_interval * 60)}</b>"
        )

    @classmethod
    async def delta(cls, idx) -> str:

        req = sql_req.new_session(expire_on_commit=False)
        result = await req.find_by(
            model.ArithmeticMean,
            bot_name=cls.bot_name,
            algorithm_id=cls.id,
        )
        return f"\n{idx}. /drop_time_{cls.id} Среднее время ожидания <b>~ {timedelta(seconds = int(round(result[0].seconds, 2) / result[0].times)) if result and result[0].times else 0}</b>"

    @classmethod
    @abstractmethod
    async def info(
        cls,
        with_title=None,
        with_commands=None,
        with_action=None,
        with_picture=None,
        manual=None,
    ) -> str:
        pass


class ConfAlgorithm1(Config):

    id = 1
    bar_interval = os.environ.get(f"BOT_BAR_INTERVAL_{id}", "5m")
    sched_interval = int(os.environ.get(f"BOT_SCHED_INTERVAL_{id}", 40))
    bar_limit = int(os.environ.get(f"BOT_BAR_LIMIT_{id}", 100))
    percent = int(os.environ.get(f"BOT_PERCENT_{id}", 100))
    path_picture = f"data/img/algorithm_№{id}.png"

    @classmethod
    async def info(
        cls,
        with_title=None,
        with_commands=None,
        with_action=None,
        with_picture=None,
        manual=None,
    ) -> str:

        delta = await cls.delta(7)
        if with_commands:
            return (
                cls.title(with_title)
                + f"\n<b>Алгоритм №{cls.id}</b> {cls.action(with_action)} {cls.picture(with_picture)}"
                + f"\n1. Сравнение с баром: <b>0</b> c <b>{cls.bar_limit - 1}</b>"
                + f"\n2. /edit_limit_1 Лимит баров: <b>{cls.bar_limit}</b>"
                + f"\n3. /edit_interval_1 Интервал бара: <b>{cls.bar_interval}</b>"
                + f"\n4. /edit_percent_1 Минимальный процент роста между 0 и {cls.bar_limit - 1}: <b>+{cls.percent}%</b>"
                + f"\n5. /edit_order_book_limit Лимит заявок в стакане: <b>{cls.order_book_limit}</b>"
                + f"\n6. Временная зона: <b>UTC+0</b>"
                + delta
                + cls.scheduler(8, manual)
                + f"\n9. Тип вывода инорфмации: <b>{cls.output.type}</b>"
            )
        else:
            return (
                cls.title(with_title)
                + f"\n<b>Алгоритм №{cls.id}</b> {cls.action(with_action)} {cls.picture(with_picture)}"
                + f"\n1. Сравнение с баром: <b>0</b> c <b>{cls.bar_limit - 1}</b>"
                + f"\n2. Лимит баров: <b>{cls.bar_limit}</b>"
                + f"\n3. Интервал бара: <b>{cls.bar_interval}</b>"
                + f"\n4. Минимальный процент роста между 0 и {cls.bar_limit - 1}: <b>+{cls.percent}%</b>"
                + f"\n5. Лимит заявок в стакане: <b>{cls.order_book_limit}</b>"
                + f"\n6. Временная зона: <b>UTC+0</b>"
                + delta
                + cls.scheduler(8, manual)
                + f"\n9. Тип вывода инорфмации: <b>{cls.output.type}</b>"
            )


class ConfAlgorithm2(Config):

    id = 2
    bar_interval = os.environ.get(f"BOT_BAR_INTERVAL_{id}", "1h")
    bar_limit = int(os.environ.get(f"BOT_BAR_LIMIT_{id}", 24))
    percent = int(os.environ.get(f"BOT_PERCENT_{id}", 10))
    bar_range = int(os.environ.get(f"BOT_BAR_RANGE_{id}", 1))
    price_ratio = int(os.environ.get(f"BOT_PRICE_RATIO_{id}", 50))
    path_picture = f"data/img/algorithm_№{id}.png"

    @classmethod
    async def info(
        cls,
        with_title=None,
        with_commands=None,
        with_action=None,
        with_picture=None,
        manual=None,
    ) -> str:

        delta = await cls.delta(8)
        if with_commands:
            return (
                cls.title(with_title)
                + f"\n<b>Алгоритм №{cls.id}</b> {cls.action(with_action)} {cls.picture(with_picture)}"
                + f"\n1. Сравнение с баром: <b>N</b> c <b>N + {cls.bar_range}</b>"
                + f"\n2. /edit_limit_2 Лимит баров: <b>{cls.bar_limit}</b>"
                + f"\n3. /edit_interval_2 Интервал бара: <b>{cls.bar_interval}</b>"
                + f"\n4. /edit_percent_2 Допустимый процент роста между <b>N</b> и <b>N</b> + <b>{cls.bar_range}</b>: <b>+{cls.percent}%</b>"
                + f"\n5. /edit_price Коэфф. для сравнения объемов цены между <b>N</b> >= (<b>N</b> + <b>{cls.bar_range}</b>) * коэфф. : <b>{cls.price_ratio}</b>"
                + f"\n6. /edit_order_book_limit Лимит заявок в стакане: <b>{cls.order_book_limit}</b>"
                + f"\n7. Временная зона: <b>UTC+0</b>"
                + delta
                + f"\n9. Тип вывода инорфмации: <b>{cls.output.type}</b>"
            )
        else:
            return (
                cls.title(with_title)
                + f"\n<b>Алгоритм №{cls.id}</b> {cls.action(with_action)} {cls.picture(with_picture)}"
                + f"\n1. Сравнение с баром: <b>N</b> c <b>N + {cls.bar_range}</b>"
                + f"\n2. Лимит баров: <b>{cls.bar_limit}</b>"
                + f"\n3. Интервал бара: <b>{cls.bar_interval}</b>"
                + f"\n4. Допустимый процент роста между <b>N</b> и <b>N</b> + <b>{cls.bar_range}</b>: <b>+{cls.percent}%</b>"
                + f"\n5. Коэфф. для сравнения объемов цены между <b>N</b> >= (<b>N</b> + <b>{cls.bar_range}</b>) * коэфф. : <b>{cls.price_ratio}</b>"
                + f"\n6. Лимит заявок в стакане: <b>{cls.order_book_limit}</b>"
                + f"\n7. Временная зона: <b>UTC+0</b>"
                + delta
                + f"\n9. Тип вывода инорфмации: <b>{cls.output.type}</b>"
            )


class ConfAlgorithm3(Config):

    id = 3
    bar_interval = os.environ.get(f"BOT_BAR_INTERVAL_{id}", "1d")
    bar_limit = int(os.environ.get(f"BOT_BAR_LIMIT_{id}", 90))
    percent = int(os.environ.get(f"BOT_PERCENT_{id}", 10))
    bar_range = int(os.environ.get(f"BOT_BAR_RANGE_{id}", 1))
    order_book_ratio = int(os.environ.get(f"BOT_ORDER_BOOK_RATIO_{id}", 5))
    path_picture = f"data/img/algorithm_№{id}.png"

    @classmethod
    async def info(
        cls,
        with_title=None,
        with_commands=None,
        with_action=None,
        with_picture=None,
        manual=None,
    ) -> str:

        delta = await cls.delta(8)
        if with_commands:
            return (
                cls.title(with_title)
                + f"\n<b>Алгоритм №{cls.id}</b> {cls.action(with_action)} {cls.picture(with_picture)}"
                + f"\n1. Сравнение с баром: <b>N</b> c <b>N + {cls.bar_range}</b>"
                + f"\n2. /edit_limit_3 Лимит баров: <b>{cls.bar_limit}</b>"
                + f"\n3. /edit_interval_3 Интервал бара: <b>{cls.bar_interval}</b>"
                + f"\n4. /edit_percent_3 Допустимый процент роста между <b>N</b> и <b>N</b> + <b>{cls.bar_range}</b>: <b>+-{cls.percent}%</b>"
                + f"\n5. /edit_order_book_limit Лимит заявок в стакане: <b>{cls.order_book_limit}</b>"
                + f"\n6. /edit_order_book_ratio Коэфф. во сколько за сумма bids/asks &gt; <b>N</b>: <b>{cls.order_book_ratio}</b>"
                + f"\n7. Временная зона: <b>UTC+0</b>"
                + delta
                + f"\n9. Тип вывода инорфмации: <b>{cls.output.type}</b>"
            )
        else:
            return (
                cls.title(with_title)
                + f"\n<b>Алгоритм №{cls.id}</b> {cls.action(with_action)} {cls.picture(with_picture)}"
                + f"\n1. Сравнение с баром: <b>N</b> c <b>N + {cls.bar_range}</b>"
                + f"\n2. Лимит баров: <b>{cls.bar_limit}</b>"
                + f"\n3. Интервал бара: <b>{cls.bar_interval}</b>"
                + f"\n4. Допустимый процент роста между <b>N</b> и <b>N</b> + <b>{cls.bar_range}</b>: <b>+-{cls.percent}%</b>"
                + f"\n5. Лимит заявок в стакане: <b>{cls.order_book_limit}</b>"
                + f"\n6. Коэфф. во сколько за сумма bids/asks &gt; <b>N</b>: <b>{cls.order_book_ratio}</b>"
                + f"\n7. Временная зона: <b>UTC+0</b>"
                + delta
                + f"\n9. Тип вывода инорфмации: <b>{cls.output.type}</b>"
            )


class ConfAlgorithm4(Config):

    id = 4
    bar_interval = os.environ.get(f"BOT_BAR_INTERVAL_{id}", "1d")
    sched_interval = int(os.environ.get(f"BOT_SCHED_INTERVAL_{id}", 60))
    bar_limit = int(os.environ.get(f"BOT_BAR_LIMIT_{id}", 10))
    bar_range = int(os.environ.get(f"BOT_BAR_RANGE_{id}", 1))
    trade_ratio = int(os.environ.get(f"BOT_TRADE_RATIO_{id}", 100))
    path_picture = f"data/img/algorithm_№{id}.png"

    @classmethod
    async def info(
        cls,
        with_title=None,
        with_commands=None,
        with_action=None,
        with_picture=None,
        manual=None,
    ) -> str:

        delta = await cls.delta(6)
        if with_commands:
            return (
                cls.title(with_title)
                + f"\n<b>Алгоритм №{cls.id}</b> {cls.action(with_action)} {cls.picture(with_picture)}"
                + f"\n1. /edit_limit_{cls.id} Лимит баров: <b>{cls.bar_limit}</b>"
                + f"\n2. /edit_interval_{cls.id} Интервал бара: <b>{cls.bar_interval}</b>"
                + f"\n3. /edit_ratio_{cls.id} Коэфф. для сравнения объемов торгов в: <b>{cls.trade_ratio}</b>"
                + f"\n4. /edit_order_book_limit Лимит заявок в стакане: <b>{cls.order_book_limit}</b>"
                + f"\n5. Временная зона <b>UTC+0</b>"
                + delta
                + cls.scheduler(7, manual)
                + f"\n8. Тип вывода инорфмации: <b>{cls.output.type}</b>"
            )
        else:
            return (
                cls.title(with_title)
                + f"\n<b>Алгоритм №{cls.id}</b> {cls.action(with_action)} {cls.picture(with_picture)}"
                + f"\n1. Лимит баров: <b>{cls.bar_limit}</b>"
                + f"\n2. Интервал бара: <b>{cls.bar_interval}</b>"
                + f"\n3. Коэфф. для сравнения объемов торгов в: <b>{cls.trade_ratio}</b>"
                + f"\n4. Лимит заявок в стакане: <b>{cls.order_book_limit}</b>"
                + f"\n5. Временная зона <b>UTC+0</b>"
                + delta
                + cls.scheduler(7, manual)
                + f"\n8. Тип вывода инорфмации: <b>{cls.output.type}</b>"
            )


class ConfAlgorithm5(Config):

    id = 5
    alias_candle_price = {
        "low": "lowest_price",
        "high": "highest_price",
        "open": "open_price",
        "close": "close_price",
    }
    bar_interval = os.environ.get(f"BOT_BAR_INTERVAL_{id}", "4h")
    sched_interval = int(os.environ.get(f"BOT_SCHED_INTERVAL_{id}", 1440))
    bar_limit = int(os.environ.get(f"BOT_BAR_LIMIT_{id}", 12))
    split = int(os.environ.get(f"BOT_SPLIT_{id}", 6))
    candle_price = str(os.environ.get(f"BOT_CANDLE_PRICE_{id}", "high"))
    bar_range = int(os.environ.get(f"BOT_BAR_RANGE_{id}", 1))
    percent = int(os.environ.get(f"BOT_PERCENT_{id}", 50))
    path_picture = f"data/img/algorithm_№{id}.png"

    @classmethod
    async def info(
        cls,
        with_title=None,
        with_commands=None,
        with_action=None,
        with_picture=None,
        manual=None,
    ) -> str:

        delta = await cls.delta(8)
        if with_commands:
            return (
                cls.title(with_title)
                + f"\n<b>Алгоритм №{cls.id}</b> {cls.action(with_action)} {cls.picture(with_picture)}"
                + f"\n1. /edit_limit_{cls.id} Лимит баров: <b>{cls.bar_limit}</b>"
                + f"\n2. /edit_interval_{cls.id} Интервал бара: <b>{cls.bar_interval}</b>"
                + f"\n3. /edit_split Разбиение на отрезки по: <b>{cls.split}</b>"
                + f"\n4. /edit_candle_price Цена бара: <b>{cls.candle_price}</b>"
                + f"\n5. /edit_percent_{cls.id} Минимальный процент совпадений в отрезке: <b>{cls.percent}%</b>"
                + f"\n6. /edit_order_book_limit Лимит заявок в стакане: <b>{cls.order_book_limit}</b>"
                + f"\n7. Временная зона <b>UTC+0</b>"
                + delta
                + cls.scheduler(9, manual)
                + f"\n10. Тип вывода инорфмации: <b>{cls.output.type}</b>"
            )
        else:
            return (
                cls.title(with_title)
                + f"\n<b>Алгоритм №{cls.id}</b> {cls.action(with_action)} {cls.picture(with_picture)}"
                + f"\n1. Лимит баров: <b>{cls.bar_limit}</b>"
                + f"\n2. Интервал бара: <b>{cls.bar_interval}</b>"
                + f"\n3. Разбиение на отрезки по: <b>{cls.split}</b>"
                + f"\n4. Цена бара: <b>{cls.candle_price}</b>"
                + f"\n5. Минимальный процент совпадений в отрезке: <b>{cls.percent}%</b>"
                + f"\n6. Лимит заявок в стакане: <b>{cls.order_book_limit}</b>"
                + f"\n7. Временная зона <b>UTC+0</b>"
                + delta
                + cls.scheduler(9, manual)
                + f"\n10. Тип вывода инорфмации: <b>{cls.output.type}</b>"
            )


class Commands:

    picture_text = "иллюстрация результата работы"
    interval_text = "изменить интервал бара (10s|1m|5m|15m|30m|1h|4h|8h|1d|7d|30d)"

    info = {
        "check": {"info": "проверка состояния бота"},
        "add_buttons": {"info": "добавить кнопки"},
        "del_buttons": {"info": "удалить кнопки"},
        "help": {
            "info": "информация о возможных командах, которыми пользователь может воспользоваться"
        },
        "stop": {"info": "выход из процесса без вызова обработчиков очистки"},
        "pause": {"info": "приостановка выполнения каких-либо команд"},
        "active": {"info": "активация всех функций бота"},
        f"algorithm_{ConfAlgorithm1.id}": {
            "info": f"поиск бумаг по алгоритму №{ConfAlgorithm1.id}",
            "commands": {
                "edit_percent_1 N": {"info": "изменить процент роста цены"},
                "edit_limit_1 N": {"info": "изменить лимит баров"},
                "edit_interval_1 N": {"info": interval_text},
                "picture_1": {"info": picture_text},
            },
        },
        f"algorithm_{ConfAlgorithm2.id}": {
            "info": f"поиск бумаг по алгоритму №{ConfAlgorithm2.id}",
            "commands": {
                "edit_price N": {"info": "изменить коэффициент объема цены"},
                "edit_percent_2 N": {"info": "изменить процент роста цены"},
                "edit_limit_2 N": {"info": "изменить лимит баров"},
                "edit_interval_2 N": {"info": interval_text},
                "picture_2": {"info": picture_text},
            },
        },
        f"algorithm_{ConfAlgorithm3.id}": {
            "info": f"поиск бумаг по алгоритму №{ConfAlgorithm3.id}",
            "commands": {
                "edit_order_book_ratio N": {
                    "info": "изменить коэффициент bids/asks &gt; <b>N</b>"
                },
                "edit_percent_3 N": {"info": "изменить процент роста цены"},
                "edit_limit_3 N": {"info": "изменить лимит баров"},
                "edit_interval_3 N": {"info": interval_text},
                "picture_3": {"info": picture_text},
            },
        },
        f"algorithm_{ConfAlgorithm4.id}": {
            "info": f"поиск бумаг по алгоритму №{ConfAlgorithm4.id}",
            "commands": {
                "edit_ratio_4 N": {"info": "изменить коэффициент объема"},
                "edit_limit_4 N": {"info": "изменить лимит баров"},
                "edit_interval_4 N": {"info": interval_text},
                "picture_4": {"info": picture_text},
            },
        },
        f"algorithm_{ConfAlgorithm5.id}": {
            "info": f"поиск бумаг по алгоритму №{ConfAlgorithm5.id}",
            "commands": {
                "edit_split N": {"info": "изменить набор баров для сравнения"},
                "edit_candle_price N": {
                    "info": f"изменить цену свечи для сравнения ({'|'.join(ConfAlgorithm5.alias_candle_price.keys())})"
                },
                "edit_percent_5 N": {"info": "изменить процент роста цены"},
                "edit_limit_5 N": {"info": "изменить лимит баров"},
                "edit_interval_5 N": {"info": interval_text},
                "picture_5": {"info": picture_text},
            },
        },
        "edit_type_output": {
            "info": f"изменить формат вывода алгоритмов ({Text.type}|{HTML.type}|{Pdf.type}|{MessegeFlow.type})"
        },
        "readme": {"info": "информация по алгоритмам"},
        "current_conf": {"info": "текущая концигурация всех алгоритмов"},
        "note currency text": {
            "info": "добавить заметку к определенной валюте (Пример: /note BTC информация)"
        },
        "list_my_notes": {"info": "список всех заметок"},
        "edit_order_book_limit N": {
            "info": "изменить лимит заявок в стакане asks/bids"
        },
        "version": {"info": "версия клиента"},
        "version_py": {"info": "версия интерпретатора python"},
        "logs": {"info": "системная информация, которую логирует бот"},
    }

    @classmethod
    def __depth(cls, data: dict, text: str, count=0) -> str:

        tab = "\t\t\t\t"
        if type(data) is dict and data:
            for k, d in data.items():
                if "info" in d:
                    text += f"{tab * count}/{k} - {d['info']}\n"
                    del d["info"]
                if d:
                    count += 1
                    for k, d2 in d.items():
                        text += f"{tab * count}{k}:\n" + cls.__depth(d2, "", count + 1)
                    count = 0
        return text
        # if type(data) is list and data:
        #     return 1 + max(self.__depth(a) for a in data)

    @classmethod
    def to_text(cls):
        info = deepcopy(cls.info)
        return cls.__depth(info, f"Commands: \n")
