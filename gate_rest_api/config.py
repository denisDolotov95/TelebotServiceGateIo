# -*- coding: utf-8 -*-
import os
import json
import secrets
from pydantic import BaseModel, RedisDsn, Field, AliasChoices


class ProductionConfig(BaseModel):
    DB_URL: str = ""
    SECRET_KEY: str = os.environ.get("SECRET_KEY") or secrets.token_hex(256)
    DEBUG: bool = True
    REDIS_URL: RedisDsn = Field(
        f"redis://{os.environ.get('REDIS_HOST')}:{os.environ.get('REDIS_PORT')}/1",
        validation_alias=AliasChoices("REDIS_URL"),
    )
    # "url": "amqp://guest:guest@172.100.100.100"}
    api_metadata: str = json.loads(
        open("./data/api_metadata.json", "r", encoding="utf-8").read()
    )
