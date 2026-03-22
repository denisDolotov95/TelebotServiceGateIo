# -*- coding: utf-8 -*-
import json
import copy
import telebot
import asyncio
import pandas
import pdfkit

from io import BytesIO
from prettytable import PrettyTable
from datetime import datetime
from functools import wraps

__all__ = [
    "calculate_delta",
    "create_byte_file",
    "return_generator",
    "SumOrderbook",
    "ContentFilter",
    "TelegramButtons",
    "Table",
    "AsyncTask",
]


def generator(payload):
    for data in payload:
        yield data


def return_generator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        payload = await func(*args, **kwargs)
        new_generator = generator(payload)
        return new_generator

    return wrapper


def create_byte_file(text, file_name, file_format):

    byte_file = BytesIO()
    byte_file.name = f"{file_name}.{file_format}"
    if file_format == "html":
        html_text = text.encode("utf-8")
        byte_file.write(html_text)
    elif file_format == "pdf":
        pdf_text = pdfkit.from_string(text)
        byte_file.write(pdf_text)
    byte_file.seek(0, 0)
    return byte_file


def calculate_delta(first_price: str, second_price: str) -> float:

    return (float(first_price) - float(second_price)) / float(second_price) * 100


class AsyncTask:

    def __init__(self, work_queue: asyncio.Queue) -> None:
        # self.name = name
        self.__payload = []
        self.__work_queue = work_queue

    async def exec(self, func) -> list:

        while not self.__work_queue.empty():
            data = await self.__work_queue.get()
            result = await func(data)
            if result:
                self.__payload.append(result)
        return self.__payload


class DockerParser:

    async def execute(self, command) -> tuple[bytes, bytes]:

        # stdout_data = subprocess.run([self.command], stdout=subprocess.PIPE, shell=True)
        proc = await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        return stdout, stderr

    def formation_column(self, data) -> list[str] | None:

        data = list(data)
        leng = len(data) - 1
        for i, char in enumerate(data):
            if i == leng:
                break
            if char == " " and data[i + 1] == " ":
                data[i] = None
            elif data[i - 1] == None and data[i + 1] != " ":
                data[i] = "|"
        return "".join([char for char in data if char != None]).split("|")

    def parse(self, stdout) -> pandas.DataFrame:

        list_text = stdout.decode("utf-8").split("\n")
        columns = self.formation_column(list_text.pop(0))
        raws = [self.formation_column(line) for line in list_text if line]
        for raw in raws:
            if len(columns) > len(raw):
                raw += (len(columns) - len(raw)) * [""]
        return pandas.DataFrame(columns=columns, data=raws)


class TelegramButtons:

    def __init__(self, payload: list[str] | dict = None) -> None:

        self.payload: list[str] | dict = payload
        self.buttons = list()

    def __clear(func):
        def wrapper(self, *args, **kwargs):

            self.buttons.clear()
            return func(self, *args, **kwargs)

        return wrapper

    @__clear
    def create_inline_keyboard(
        self, *args, **kwargs
    ) -> telebot.types.InlineKeyboardMarkup:

        keyboard = telebot.types.InlineKeyboardMarkup(*args, **kwargs)
        for key, data in self.payload.items():
            self.buttons.append(
                telebot.types.InlineKeyboardButton(
                    text=key,
                    callback_data=json.dumps(data),
                )
            )
        return keyboard.add(*self.buttons)

    @__clear
    def create_reply_keyboard(
        self, *args, **kwargs
    ) -> telebot.types.ReplyKeyboardMarkup:

        keyboard = telebot.types.ReplyKeyboardMarkup(*args, **kwargs)
        for data in self.payload:
            self.buttons.append(telebot.types.KeyboardButton(data))
        return keyboard.add(*self.buttons)


class Table:

    def __init__(self, data: dict, pretty: PrettyTable = None):

        self.data = copy.deepcopy(data)
        self.pretty = pretty if pretty else PrettyTable()

    def get_string(self, total_items_row=3, *args, **kwargs):

        keys = [f"{key}:" for key in self.data.keys()]
        values = [value for value in self.data.values()]
        for i in range(0, len(self.data), total_items_row):
            length = len(keys[i : i + total_items_row])
            split_keys = keys[i : i + total_items_row]
            split_values = values[i : i + total_items_row]
            if length < total_items_row:
                split_keys += [""] * (total_items_row - length)
                split_values += [""] * (total_items_row - length)
            self.pretty.add_row(split_keys)
            self.pretty.add_row(split_values, divider=True)
        return f"<pre>{self.pretty.get_string(*args, **kwargs)}</pre>"


class ContentFilter:

    @staticmethod
    def s_filter(payload: list, func=None) -> list:

        new_data = list()
        for data in payload:
            if func(data):
                new_data.append(data)
        return new_data

    def __init__(self, filters: list = None) -> None:

        self._filters = list()
        if filters is not None:
            self._filters += filters

    def filter(self, payload: list = None) -> list:

        new_payload = list(payload)
        for filter in self._filters:
            new_payload = ContentFilter.s_filter(new_payload, filter)
        return new_payload


class SumOrderbook:

    @staticmethod
    def s_update_date(date: str | int):

        try:
            if isinstance(date, str | int):
                return datetime.fromtimestamp(int(date)).__str__()
        except (OSError, ValueError):
            return datetime.fromtimestamp(int(date) / 1000).__str__()

    def __init__(self, data: dict) -> None:

        self.data = copy.deepcopy(data)

    def update_date(self, key: str) -> str | None:

        try:
            if self.data.get(key):
                return datetime.fromtimestamp(int(self.data[key])).__str__()
        except (OSError, ValueError):
            return datetime.fromtimestamp(int(self.data[key]) / 1000).__str__()

    def first(self, key: str) -> float | int:

        return float(self.data[key][0].get("price")) * float(
            self.data[key][0].get("amount")
        ) if self.data[key] else 0

    def sum(self, key: str) -> float | int:

        total = set()
        for data in self.data.get(key) if key in self.data else []:
            total.add(float(data.get("price")) * float(data.get("amount")))
        return round(sum(total), 2)

    def more_then(self, first: float | int, second: float | int) -> float | int:

        return round(first / second, 2) if second else 0
