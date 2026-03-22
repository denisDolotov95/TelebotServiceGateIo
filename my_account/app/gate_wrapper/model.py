# -*- coding: utf-8 -*-
import typing
from pydantic import BaseModel

__all__ = [   
    "Account", 
    "AccountBook", 
    "Ask", 
    "Bid", 
    "Candlestick", 
    "Cbbc", 
    "Common", 
    "CrossMargin", 
    "Currency", 
    "CurrencyPair", 
    "Delivery", 
    "Details", 
    "Finance", 
    "Futures", 
    "Margin", 
    "OpenOrders", 
    "Order", 
    "OrderBook", 
    "Quant", 
    "ShortOrder", 
    "Spot", 
    "Ticker", 
    "Total", 
    "TotalBalance", 
    "Trade", 
    "Warrant"
]

class Ticker(BaseModel):
    currency_pair: str | None = None
    last: str | None = None
    lowest_ask: str | None = None
    highest_bid: str | None = None
    change_percentage: str | None = None
    change_utc0: str | None = None
    change_utc8: str | None = None
    base_volume: str | None = None
    quote_volume: str | None = None
    high_24h: str | None = None
    low_24h: str | None = None
    etf_net_value: str | None = None
    etf_pre_net_value: str | None = None
    etf_pre_timestamp: int | None = None
    etf_leverage: str | None = None


class Account(BaseModel):
    currency: str | None = None
    available: str | None = None
    locked: str | None = None
    update_id: int | None = None


class AccountBook(BaseModel):
    id: str | None = None
    time: int = None
    currency: str | None = None
    change: str | None = None
    balance: str | None = None
    type: str | None = None
    text: str | None = None


class Currency(BaseModel):
    currency: str | None = None
    delisted: bool = None
    withdraw_disabled: bool = None
    withdraw_delayed: bool = None
    deposit_disabled: bool = None
    trade_disabled: bool = None
    chain: str | None = None


class CurrencyPair(BaseModel):
    id: str | None = None
    base: str | None = None
    quote: str | None = None
    fee: str | None = None
    min_base_amount: str | None = None
    min_quote_amount: str | None = None
    max_base_amount: str | None = None
    max_quote_amount: str | None = None
    amount_precision: int = None
    precision: int = None
    trade_status: str | None = None
    sell_start: int = None
    buy_start: int = None


class Trade(BaseModel):
    id: int | None = None
    create_time: int | None = None
    create_time_ms: float | None = None
    order_id: int | None = None
    side: str | None = None
    role: str | None = None
    amount: str | None = None
    price: str | None = None
    fee: str | None = None
    fee_currency: str | None = None
    point_fee: str | None = None
    gt_fee: str | None = None
    sequence_id: int | None = None
    text: str | None = None


class Ask(BaseModel):
    price: str | None = None
    amount: str | None = None


class Bid(BaseModel):
    price: str | None = None
    amount: str | None = None


class OrderBook(BaseModel):
    id: int | None = None
    current: int = None
    update: int = None
    asks: typing.List[Ask] = None
    bids: typing.List[Bid] = None


class ShortOrder(BaseModel):
    id: str | None = None
    text: str | None = None
    create_time: str | None = None
    update_time: str | None = None
    currency_pair: str | None = None
    status: str | None = None
    type: str | None = None
    account: str | None = None
    side: str | None = None
    amount: str | None = None
    price: str | None = None
    time_in_force: str | None = None
    left: str | None = None
    filled_total: str | None = None
    fee: str | None = None
    fee_currency: str | None = None
    point_fee: str | None = None
    gt_fee: str | None = None
    gt_discount: bool = None
    rebated_fee: str | None = None
    rebated_fee_currency: str | None = None


class Order(ShortOrder):
    amend_text: str | None = None
    create_time_ms: int = None
    update_time_ms: int = None
    iceberg: str | None = None
    filled_amount: str | None = None
    fill_price: str | None = None
    avg_deal_price: str | None = None
    gt_maker_fee: str | None = None
    gt_taker_fee: str | None = None
    finish_as: str | None = None


class OpenOrders(BaseModel):
    currency_pair: str | None = None
    total: str | None | int = None
    orders: typing.List[ShortOrder] = None


class Candlestick(BaseModel):
    """K-line data for each time granularity, arranged from left to right:
    - Unix timestamp with second precision
    - Trading volume in quote currency
    - Closing price
    - Highest price
    - Lowest price
    - Opening price
    - Trading volume in base currency
    - Whether the window is closed; true indicates the end of this segment of candlestick chart data, false indicates that this segment of candlestick chart data is not yet complete
            Args:
                BaseModel (_type_): _description_
    """

    unix_timestamp: str | None = None
    trade_volume_in_quote: float = None
    close_price: str | None = None
    highest_price: str | None = None
    lowest_price: str | None = None
    open_price: str | None = None
    trade_volume_in_base: float = None
    window_is_closed: bool = None


class Common(BaseModel):
    currency: str | None = None
    amount: str | None = None


class CrossMargin(Common):
    pass


class Spot(Common):
    pass


class Finance(Common):
    pass


class Margin(Common):
    borrowed: str | None = None


class Quant(Common):
    pass


class Futures(Common):
    unrealised_pnl: str | None = None


class Delivery(Common):
    unrealised_pnl: str | None = None


class Warrant(Common):
    pass


class Cbbc(Common):
    pass


class Total(Common):
    unrealised_pnl: str | None = None
    borrowed: str | None = None


class Details(BaseModel):
    cross_margin: CrossMargin = None
    spot: Spot = None
    finance: Finance = None
    margin: Margin = None
    quant: Quant = None
    futures: Futures = None
    delivery: Delivery = None
    warrant: Warrant = None
    cbbc: Cbbc = None


class TotalBalance(BaseModel):
    details: Details
    total: Total