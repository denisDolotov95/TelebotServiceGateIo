# -*- coding: utf-8 -*-
import logging
import os
import fastapi
import uvicorn
import multiprocessing

import logging.handlers as l_handl
from config import ProductionConfig


if "log" not in os.listdir():
    os.mkdir(os.path.join(os.getcwd(), "log"))

rot_file_handler = l_handl.RotatingFileHandler(
    "./log/gate_rest_api.log",
    maxBytes=50 * 1024 * 1024,
    backupCount=10,
    encoding="utf-8",
)

logging.basicConfig(
    handlers=[rot_file_handler],
    format=(
        "[%(asctime)s] (%(filename)s:%(lineno)d %(threadName)s) "
        '%(levelname)s - %(name)s: "%(message)s"'
    ),
)

for log in (logging.getLogger(n) for n in logging.root.manager.loggerDict):
    log.setLevel(logging.DEBUG)

app_conf = ProductionConfig()

app = fastapi.FastAPI(**app_conf.api_metadata, debug=app_conf.DEBUG)

from exceptions import *
from views import *

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.environ.get("FASTAPI_PORT", 3500)),
        workers=multiprocessing.cpu_count(),
    )
