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
    "Config",
    "DB_CONFIGURATION",
    "GATE_CONFIGURATION",
    "LOG_FILE_NAME",
    "CONTAINER_ID",
    "BOT_NAME",
    "TELEGRAM_BOT",
    "api_client",
    "bot",
    "engine",
    "sql_req",
]

CONTAINER_ID = os.environ.get("CONTAINER_ID", 0)

BOT_NAME = os.environ.get("BOT_NAME", "my_pump_stock")

LOG_FILE_NAME = f"{CONTAINER_ID}_{BOT_NAME}"

# DB_CONFIGURATION = {
#     "driver": os.environ.get("DB_DRIVER", "postgresql"),
#     "username": os.environ.get("DB_USERNAME", "gate_io"),
#     "password": os.environ.get("DB_PASSWORD", "A510B467E9DBE5E8ADA6C466429099E6"),
#     "host": os.environ.get("DB_HOST", "192.168.0.110"),
#     "port": int(os.environ.get("DB_PORT", 5432)),
#     "service_name": os.environ.get("DB_SERVICE_NAME", "gate_io"),
#     "async_req": True,
# }

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
    # "8150bdc658836c1cb07e4b5380f564e3"
    "key": os.environ.get("GATE_KEY", "19aeac7ee171b2d"),
    # "75c3b0e31e1fdeee53d8b27eefbc22174d99a0854832fa6f5f7b3633c204d22b"
    "secret": os.environ.get(
        "GATE_SECRET",
        "d07a4fb149f8b19ea857965a0fa6a10b1",
    ),
}

api_client = gate_api.ApiClient(gate_api.Configuration(**GATE_CONFIGURATION))


TELEGRAM_BOT = {
    "host": os.environ.get("TELEGRAM_HOST", "https://api.telegram.org"),
    "token": os.environ.get(
        "TELEGRAM_BOT_TOKEN", "6798179326:AAHYApHoklx11gyT"
    ),
    "chat_id": int(os.environ.get("TELEGRAM_CHAT_ID", "58000")),
    "connect_timeout": int(os.environ.get("TELEGRAM_CONN_TIME", 60)),
}

bot = async_telebot.AsyncTeleBot(TELEGRAM_BOT["token"])


class Config(ABC):

    id = 0
    bot_name = BOT_NAME
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
    async def info(cls, *args, **kwargs) -> str:
        pass


class ConfAlgorithm1(Config):

    id = 1
    bar_interval = os.environ.get("BOT_BAR_INTERVAL", "5m")
    sched_interval = int(os.environ.get("BOT_SCHED_INTERVAL", 5))
    bar_limit = int(os.environ.get("BOT_BAR_LIMIT", 100))
    percent = int(os.environ.get("BOT_PERCENT", 100))
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
                + f"\n4. /edit_percent_1 Минимальный процент роста между <b>0</b> и <b>{cls.bar_limit - 1}</b>: <b>+{cls.percent}%</b>"
                + f"\n5. /edit_order_book_limit Лимит заявок в стакане: <b>{cls.order_book_limit}</b>"
                + f"\n6. Временная зона: <b>UTC+0</b>"
                + delta
                + cls.scheduler(8, manual)
            )
        else:
            return (
                cls.title(with_title)
                + f"\n<b>Алгоритм №{cls.id}</b> {cls.action(with_action)} {cls.picture(with_picture)}"
                + f"\n1. Сравнение с баром: <b>0</b> c <b>{cls.bar_limit - 1}</b>"
                + f"\n2. Лимит баров: <b>{cls.bar_limit}</b>"
                + f"\n3. Интервал бара: <b>{cls.bar_interval}</b>"
                + f"\n4. Минимальный процент роста между <b>0</b> и <b>{cls.bar_limit - 1}</b>: <b>+{cls.percent}%</b>"
                + f"\n5. Лимит заявок в стакане: <b>{cls.order_book_limit}</b>"
                + f"\n6. Временная зона: <b>UTC+0</b>"
                + delta
                + cls.scheduler(8, manual)
            )


class ConfAlgorithm2(Config):

    id = 2

    @classmethod
    async def info(
        cls,
        with_title=None,
        with_commands=None,
        with_action=None,
        with_picture=None,
        manual=None,
    ) -> str:

        delta = await cls.delta(3)
        if with_commands:
            return (
                cls.title(with_title)
                + f"\n<b>Алгоритм №{cls.id}</b> {cls.action(with_action)} {cls.picture(with_picture)}"
                + f"\n1. Лимит заявок в стакане: <b>{cls.order_book_limit}</b>"
                + f"\n2. Временная зона: <b>UTC+0</b>"
                + delta
            )
        else:
            return (
                cls.title(with_title)
                + f"\n<b>Алгоритм №{cls.id}</b> {cls.action(with_action)} {cls.picture(with_picture)}"
                + f"\n1. Лимит заявок в стакане: <b>{cls.order_book_limit}</b>"
                + f"\n2. Временная зона: <b>UTC+0</b>"
                + delta
            )


class Commands:

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
        "algorithm_1": {
            "info": "поиск валюты по алгоритму №1",
            "commands": {
                "edit_percent_1 N": {"info": "изменить процент"},
                "edit_limit_1 N": {"info": "изменить лимит баров"},
                "edit_interval_1 N": {
                    "info": "изменить интервал бара (10s|1m|5m|15m|30m|1h|4h|8h|1d|7d|30d)"
                },
                "picture_1": {"info": "иллюстрация результата работы"},
            },
        },
        "algorithm_2": {
            "info": "поиск валюты по алгоритму №2",
            "commands": {"picture_2": {"info": "иллюстрация результата работы"}},
        },
        "readme": {"info": "информация по алгоритмам"},
        "current_conf": {"info": "текущая концигурация всех алгоритмов"},
        "list_my_spots": {"info": "список купленых криптовалют"},
        "note currency text": {
            "info": "добавить заметку к определенной валюте (Пример: /note BTC информация)"
        },
        "list_my_notes": {"info": "список всех заметок"},
        "excluded_spots": {"info": "исключить из проверки криптовалюту"},
        "clear_excluded_spots": {
            "info": "очистить список исключенных из проверки криптовалют"
        },
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
