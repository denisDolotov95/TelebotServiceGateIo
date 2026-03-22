# -*- coding: utf-8 -*-
import os
import gate_api

from . import spot
from . import wallet


def create_instanse(
    _type: wallet.Wallet | spot.Spot,
    key: str = None,
    proxy: str = None,
    secret: str = None,
    host="https://api.gateio.ws/api/v4",
) -> wallet.Wallet | spot.Spot:

    GATE_CONFIGURATION: dict[str, str] = {
        "host": host if host else os.environ.get("GATE_HOST", host),
        "key": key if key else os.environ.get("GATE_KEY", key),
        "secret": (
            secret
            if secret
            else os.environ.get(
                "GATE_SECRET",
                secret,
            )
        )
        # "proxy": (
        #     proxy
        #     if proxy
        #     else os.environ.get(
        #         "GATE_PROXY",
        #         proxy,
        #     )
        # ),
    }
    gate_conf = gate_api.Configuration(**GATE_CONFIGURATION)
    # if proxy:
    #     gate_conf.proxy = os.environ.get("PROXY_URL", proxy)
    gate_api_client = gate_api.ApiClient(gate_conf)
    return _type(gate_api_client)
