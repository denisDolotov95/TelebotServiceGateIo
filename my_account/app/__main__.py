# -*- coding: utf-8 -*-
import logging
import os
import asyncio

# import util

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from logging.handlers import RotatingFileHandler

from config import *
from runners import *
from telebot_handler import *


os.chdir("app")


if "log" not in os.listdir():
    os.mkdir(os.path.join(os.getcwd(), "log"))


if "data" not in os.listdir():
    os.mkdir(os.path.join(os.getcwd(), "data"))


for log in (logging.getLogger(n) for n in logging.root.manager.loggerDict):
    if log.name == "TeleBot":
        log.setLevel(logging.INFO)
    else:
        log.setLevel(logging.DEBUG)


rot_file_handler = RotatingFileHandler(f"./log/{LOG_FILE_NAME}.log",
                                       maxBytes=10*1024*1024,
                                       backupCount=3,
                                       encoding="utf-8")


logging.basicConfig(
    level=logging.DEBUG,
    # filename=f"./log/{CONTAINER_ID}_{BOT_NAME.replace('.txt', '')}.log",
    # filemode="a",
    handlers=[rot_file_handler],
    format='[%(asctime)s] (%(filename)s:%(lineno)d %(threadName)s) %(levelname)s - %(name)s: "%(message)s"',
)


async def start():

    scheduler = AsyncIOScheduler()
    scheduler.add_job(action, "interval", minutes=SCHED_INTERVAL)
    scheduler.add_job(action_2, "interval", minutes=SCHED_INTERVAL_2)
    # scheduler.add_job(action_2, "interval", minutes=1)
    scheduler.print_jobs()
    # await action_2()
    scheduler.start()
    

    # buttons = util.TelegramButtons(["/help"])
    # await bot.send_message(
    #     TELEGRAM_BOT["chat_id"],
    #     "A keyboard has been added.",
    #     reply_markup=buttons.create_reply_keyboard(
    #         resize_keyboard=True,
    #     ),
    #     # disable_notification=True,
    # )

    # запускаем пулинг
    await bot.polling(non_stop=True, interval=1, timeout=TELEGRAM_BOT["connect_timeout"])

    # run_bot()

asyncio.run(start())