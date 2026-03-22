# -*- coding: utf-8 -*-
import os

from datetime import datetime

from sqlalchemy import Column, MetaData
from sqlalchemy.dialects.postgresql import *
from sqlalchemy.orm import DeclarativeBase

# from werkzeug.security import check_password_hash, generate_password_hash


class Base(DeclarativeBase):
    pass
    # metadata = MetaData(schema=os.environ.get("DB_SCHEMA", "prod"))


class User(Base):

    __tablename__ = "user"

    # __table_args__ = {"schema": "prod"}

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    t_user_id = Column(BIGINT, nullable=False)
    t_chat_id = Column(BIGINT, nullable=False)
    t_first_name = Column(TEXT)
    t_last_name = Column(TEXT)
    t_username = Column(TEXT)
    t_is_bot = Column(BOOLEAN)
    t_language_code = Column(VARCHAR)
    email = Column(TEXT)
    registr = Column(BOOLEAN)
    varific = Column(BOOLEAN)
    role = Column(VARCHAR)
    ban = Column(BOOLEAN)
    unix_time = Column(INTEGER)

    def __init__(
        self,
        t_user_id,
        t_chat_id,
        t_first_name=None,
        t_last_name=None,
        t_username=None,
        t_is_bot=None,
        t_language_code=None,
        registr=None,
        varific=None,
        email=None,
        ban=None,
        role="user",
    ):

        self.t_user_id = t_user_id
        self.t_chat_id = t_chat_id
        self.t_first_name = t_first_name
        self.t_last_name = t_last_name
        self.t_username = t_username
        self.t_language_code = t_language_code
        self.t_is_bot = t_is_bot
        self.email = email
        self.registr = registr
        self.varific = varific
        self.role = role
        self.ban = ban
        self.unix_time = datetime.now().timestamp()

    def __repr__(self):

        return f"User(id={self.id}, t_user_id={self.t_user_id}, unix_time={self.unix_time})"

    def __str__(self):

        return f"id={self.id}, t_user_id={self.t_user_id},  unix_time={datetime.fromtimestamp(self.unix_time).__str__()}"


class Note(Base):

    __tablename__ = "note"

    # __table_args__ = {"schema": "prod"}

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    t_user_id = Column(BIGINT, nullable=False)
    text = Column(TEXT)
    currency = Column(TEXT, nullable=False)
    unix_time = Column(INTEGER)

    def __init__(self, t_user_id, currency, text=None):

        self.t_user_id = t_user_id
        self.text = text
        self.currency = currency
        self.unix_time = datetime.now().timestamp()

    def __repr__(self):

        return f"Note(id={self.id}, t_user_id={self.t_user_id}, text='{self.text}', currency='{self.currency}', unix_time={self.unix_time})"

    def __str__(self):

        return f"id={self.id}, t_user_id={self.t_user_id}, text='{self.text}', currency='{self.currency}', unix_time={datetime.fromtimestamp(self.unix_time).__str__()}"


class ArithmeticMean(Base):

    __tablename__ = "arithmetic_mean"

    # __table_args__ = {"schema": "prod"}

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    t_user_id = Column(BIGINT, nullable=False)
    seconds = Column(REAL, nullable=False)
    times = Column(BIGINT, nullable=False)
    bot_name = Column(TEXT, nullable=False)
    algorithm_id = Column(INTEGER, nullable=False)
    unix_time = Column(INTEGER)

    def __init__(self, t_user_id, seconds, times, bot_name, algorithm_id):

        self.t_user_id = t_user_id
        self.seconds = seconds
        self.times = times
        self.bot_name = bot_name
        self.algorithm_id = algorithm_id
        self.unix_time = datetime.now().timestamp()

    def __repr__(self):

        return f"ArithmeticMean(id={self.id}, user_id={self.user_id}, seconds='{self.seconds}', times='{self.times}', unix_time={self.unix_time})"

    def __str__(self):

        return f"id={self.id}, user_id={self.user_id}, seconds='{self.seconds}', times='{self.times}', unix_time={datetime.fromtimestamp(self.unix_time).__str__()}"


class AllPumpStocks(Base):

    __tablename__ = "all_pamp_stocks"

    # __table_args__ = {"schema": "prod"}

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    currency_pair = Column(TEXT, nullable=False)
    last = Column(TEXT)
    lowest_ask = Column(TEXT)
    highest_bid = Column(TEXT)
    change_percentage = Column(TEXT)
    change_utc0 = Column(TEXT)
    change_utc8 = Column(TEXT)
    base_volume = Column(TEXT)
    quote_volume = Column(TEXT)
    high_24h = Column(TEXT)
    low_24h = Column(TEXT)
    etf_net_value = Column(TEXT)
    etf_pre_net_value = Column(TEXT)
    etf_pre_timestamp = Column(BIGINT)
    etf_leverage = Column(TEXT)
    algorithm_id = Column(SMALLINT, nullable=False)
    t_user_id = Column(BIGINT, nullable=False)
    bot_name = Column(TEXT, nullable=False)
    unix_time = Column(INTEGER)

    def __init__(
        self,
        t_user_id,
        bot_name,
        algorithm_id,
        currency_pair,
        last=None,
        lowest_ask=None,
        highest_bid=None,
        change_percentage=None,
        change_utc0=None,
        change_utc8=None,
        base_volume=None,
        quote_volume=None,
        high_24h=None,
        low_24h=None,
        etf_net_value=None,
        etf_pre_net_value=None,
        etf_pre_timestamp=None,
        etf_leverage=None,
    ):

        self.currency_pair = currency_pair
        self.last = last
        self.lowest_ask = lowest_ask
        self.highest_bid = highest_bid
        self.change_percentage = change_percentage
        self.change_utc0 = change_utc0
        self.change_utc8 = change_utc8
        self.base_volume = base_volume
        self.quote_volume = quote_volume
        self.high_24h = high_24h
        self.low_24h = low_24h
        self.etf_net_value = etf_net_value
        self.etf_pre_net_value = etf_pre_net_value
        self.etf_pre_timestamp = etf_pre_timestamp
        self.etf_leverage = etf_leverage
        self.bot_name = bot_name
        self.algorithm_id = algorithm_id
        self.t_user_id = t_user_id
        self.unix_time = datetime.now().timestamp()

    def __repr__(self):

        return f"AllPumpStocks(id={self.id}, change_percentage={self.change_percentage}, bot_name='{self.bot_name}', algorithm_id='{self.algorithm_id}', unix_time={self.unix_time})"

    def __str__(self):

        return f"id={self.id}, change_percentage={self.change_percentage}, bot_name='{self.bot_name}', algorithm_id='{self.algorithm_id}', unix_time={datetime.fromtimestamp(self.unix_time).__str__()}"
