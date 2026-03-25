# -*- coding: utf-8 -*-
import os
import gate_api

from telebot import async_telebot

SCHED_INTERVAL = int(os.environ.get("BOT_SCHED_INTERVAL", 240))

SCHED_INTERVAL_2 = int(os.environ.get("BOT_SCHED_INTERVAL_2", 360))

CONTAINER_ID = os.environ.get("CONTAINER_ID", 0)

BOT_NAME = os.environ.get("BOT_NAME", "my_account")

LOG_FILE_NAME = f"{CONTAINER_ID}_{BOT_NAME}"

GATE_DOMAIN = 'https://www.gate.io'

BROWSER_DOMAIN =  os.environ.get("BROWSER_DOMAIN", 'http://:4444/wd/hub')

LOCAL_GATE_API_IP= os.environ.get("LOCAL_GATE_REST_API_IP", "192.168.0.103")
LOCAL_GATE_API_PORT= os.environ.get("LOCAL_GATE_REST_API_PORT", "3501")
GATE_API_DOMAIN = f"{LOCAL_GATE_API_IP}:{LOCAL_GATE_API_PORT}"

INFO_COMMANDS = {
    "add_buttons": {"info": "добавить кнопки"},
    "del_buttons": {"info": "удалить кнопки"},
    "logs": {"info": "системная информация, которую логирует бот"},
    "check_delisted_info": {"info": "информация о делистинге"},
    "help": {
        "info": "информация о возможных командах, которыми пользователь может воспользоваться"
    },
    "stop": {"info": "выход из процесса без вызова обработчиков очистки"}
}

TELEGRAM_BOT = {
    "host": os.environ.get("TELEGRAM_HOST", "https://api.telegram.org"),
    "token": os.environ.get(
        "TELEGRAM_BOT_TOKEN", "7228013034:AAGq5gsii2"
    ),
    "chat_id": int(os.environ.get("TELEGRAM_CHAT_ID", "58000")),
    "connect_timeout": int(os.environ.get("TELEGRAM_CONN_TIME", 60))
}

bot = async_telebot.AsyncTeleBot(TELEGRAM_BOT["token"])

GATE_CONFIGURATION = {
    "host": os.environ.get("GATE_HOST", "https://api.gateio.ws/api/v4"),
    "key": os.environ.get("GATE_KEY", "2c4ffa1c8b3f6a935b978e8a47a67e5f"),
    "secret": os.environ.get(
        "GATE_SECRET",
        "ffa60f500082d0151e7df34fec0352110",
    ),
}

api_client = gate_api.ApiClient(gate_api.Configuration(**GATE_CONFIGURATION))