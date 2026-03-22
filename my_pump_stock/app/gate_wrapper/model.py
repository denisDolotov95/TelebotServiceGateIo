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
    currency_pair: str = None
    last: str = None
    lowest_ask: str = None
    highest_bid: str = None
    change_percentage: str = None
    change_utc0: str | None = None
    change_utc8: str | None = None
    base_volume: str = None
    quote_volume: str = None
    high_24h: str = None
    low_24h: str = None
    etf_net_value: str | None = None
    etf_pre_net_value: str | None = None
    etf_pre_timestamp: int | None = None
    etf_leverage: str | None = None


class Account(BaseModel):
    currency: str = None
    available: str = None
    locked: str = None
    update_id: int = None


class AccountBook(BaseModel):
    id: str = None
    time: int = None
    currency: str = None
    change: str = None
    balance: str = None
    type: str = None
    text: str = None


class Currency(BaseModel):
    currency: str = None
    delisted: bool = None
    withdraw_disabled: bool = None
    withdraw_delayed: bool = None
    deposit_disabled: bool = None
    trade_disabled: bool = None
    chain: str = None


class CurrencyPair(BaseModel):
    id: str = None
    base: str = None
    quote: str = None
    fee: str = None
    min_base_amount: str | None = None
    min_quote_amount: str | None = None
    max_base_amount: str | None = None
    max_quote_amount: str | None = None
    amount_precision: int = None
    precision: int = None
    trade_status: str = None
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
    price: str = None
    amount: str = None


class Bid(BaseModel):
    price: str = None
    amount: str = None


class OrderBook(BaseModel):
    id: int | None = None
    current: int = None
    update: int = None
    asks: typing.List[Ask] = None
    bids: typing.List[Bid] = None


class ShortOrder(BaseModel):
    id: str = None
    text: str = None
    create_time: str = None
    update_time: str = None
    currency_pair: str = None
    status: str = None
    type: str = None
    account: str = None
    side: str = None
    amount: str = None
    price: str = None
    time_in_force: str = None
    left: str = None
    filled_total: str = None
    fee: str = None
    fee_currency: str = None
    point_fee: str = None
    gt_fee: str = None
    gt_discount: bool = None
    rebated_fee: str = None
    rebated_fee_currency: str = None


class Order(ShortOrder):
    amend_text: str = None
    create_time_ms: int = None
    update_time_ms: int = None
    iceberg: str = None
    filled_amount: str = None
    fill_price: str = None
    avg_deal_price: str = None
    gt_maker_fee: str = None
    gt_taker_fee: str = None
    finish_as: str = None


class OpenOrders(BaseModel):
    currency_pair: str = None
    total: str | int = None
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

    unix_timestamp: str = None
    trade_volume_in_quote: float = None
    close_price: str = None
    highest_price: str = None
    lowest_price: str = None
    open_price: str = None
    trade_volume_in_base: float = None
    window_is_closed: bool = None


class Common(BaseModel):
    currency: str = None
    amount: str = None


class CrossMargin(Common):
    pass


class Spot(Common):
    pass


class Finance(Common):
    pass


class Margin(Common):
    borrowed: str = None


class Quant(Common):
    pass


class Futures(Common):
    unrealised_pnl: str = None


class Delivery(Common):
    unrealised_pnl: str = None


class Warrant(Common):
    pass


class Cbbc(Common):
    pass


class Total(Common):
    unrealised_pnl: str = None
    borrowed: str = None


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