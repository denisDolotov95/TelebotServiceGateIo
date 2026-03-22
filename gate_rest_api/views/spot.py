# -*- coding: utf-8 -*-
import os

from typing import List, Literal
from fastapi import Depends
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from redis import asyncio as aioredis


import model as api_model

from app import app
from gate_wrapper import spot, model as gate_model, create_instanse
from config import ProductionConfig


@app.on_event("startup")
async def startup():

    redis = aioredis.from_url(ProductionConfig().REDIS_URL)
    await FastAPILimiter.init(redis)


@app.post("/spot/currency_pair", tags=["Spot"])
async def currency_pair(
    payload: api_model.Payload,
    currency_pair: str,
) -> gate_model.CurrencyPair | None:

    return await create_instanse(
        spot.Spot, payload.security.key, payload.security.proxy, payload.security.secret
    ).currency_pair(
        currency_pair,
    )


@app.post("/spot/cancel_orders", tags=["Spot"])
async def cancel_orders(
    data: api_model.Security, currency_pair: str
) -> List[gate_model.Order] | None:

    return await create_instanse(
        spot.Spot, data.key, data.proxy, data.secret
    ).cancel_orders(
        currency_pair=currency_pair,
    )


@app.post("/spot/orders", tags=["Spot"])
async def orders(
    data: api_model.Security,
    currency_pair: str,
    status: Literal["open", "finished"],
) -> List[gate_model.Order] | None:

    return await create_instanse(
        spot.Spot, data.key, data.proxy, data.secret
    ).list_orders(
        currency_pair,
        status,
    )


@app.post("/spot/currency_pairs", tags=["Spot"])
async def currency_pairs(
    data: api_model.Security,
) -> List[gate_model.CurrencyPair] | None:

    return await create_instanse(
        spot.Spot, data.key, data.proxy, data.secret
    ).list_currency_pairs()


@app.post("/spot/spot_accounts", tags=["Spot"])
async def spot_accounts(
    data: api_model.Security, currency: str = None
) -> List[gate_model.Account] | None:

    return await create_instanse(
        spot.Spot, data.key, data.proxy, data.secret
    ).list_spot_accounts(
        currency=currency,
    )


@app.post("/spot/spot_account_book", tags=["Spot"])
async def spot_account_book(
    data: api_model.Security, currency: str = None
) -> List[gate_model.AccountBook] | None:

    return await create_instanse(
        spot.Spot, data.key, data.proxy, data.secret
    ).list_spot_account_book(
        currency=currency,
    )


@app.post("/spot/trades", tags=["Spot"])
async def trades(
    data: api_model.Security, currency_pair: str
) -> List[gate_model.Trade] | None:

    return await create_instanse(
        spot.Spot, data.key, data.proxy, data.secret
    ).list_trades(
        currency_pair,
    )


@app.post("/spot/tickers", tags=["Spot"])
async def tickers(
    data: api_model.Security, currency_pair: str
) -> List[gate_model.Ticker] | None:

    return await create_instanse(
        spot.Spot, data.key, data.proxy, data.secret
    ).list_tickers(
        currency_pair=currency_pair,
    )


@app.post("/spot/order_book", tags=["Spot"])
async def order_book(
    payload: api_model.Payload, currency_pair: str
) -> spot.OrderBook | None:

    return await create_instanse(
        spot.Spot,
        **(
            payload.security.model_dump()
            if payload.model_dump().get("security")
            else {}
        ),
    ).order_book(
        **payload.data.model_dump(),
        currency_pair=currency_pair,
    )


@app.post("/spot/all_open_orders", tags=["Spot"])
async def all_open_orders(
    data: api_model.Security,
) -> List[gate_model.OpenOrders] | None:

    return await create_instanse(
        spot.Spot, data.key, data.proxy, data.secret
    ).list_all_open_orders()


@app.post("/spot/candlesticks", tags=["Spot"])
async def candlesticks(
    payload: api_model.Payload,
    currency_pair: str,
    limiter=Depends(RateLimiter(times=os.cpu_count(), seconds=5)),
) -> List[gate_model.Candlestick] | None:

    return await create_instanse(
        spot.Spot,
        **payload.security.model_dump(),
    ).list_candlesticks(
        **payload.data.model_dump(),
        currency_pair=currency_pair,
        _request_timeout=(
            payload.connect.timeout,
            payload.connect.read_timeout,
        ),
    )
