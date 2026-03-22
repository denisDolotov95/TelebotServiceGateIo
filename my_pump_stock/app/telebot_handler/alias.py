# -*- coding: utf-8 -*-
import random

__all__ = [
    "ACTION",
    "ALGORITHM",
    "BACK",
    "CANCEL_ALL_ORDERS",
    "CERTAIN_LIST_MY_SPOTS",
    "CERTAIN_LIST_MY_NOTES",
    "CHECK_CURRENT_ORDER_BOOK",
    "UNIQ_TEXT_IN_NOTES",
    "LIST_UNIQ_TEXT_IN_NOTES",
    "CLEAR_NOTE",
    "CURRENT",
    "DELETE_MESSAGE",
    "EDIT_NOTE",
    "EXCLUDE_FROM_ALGORITHM",
    "FUNCTIONS_SPOT",
    "ID",
    "INCLUDE_TO_ALGORITHM",
    "LIST_NOTE",
    "LIST_ORDER",
    "MORE_INFO",
    "NOTE",
    "UPDATE_CURRENT",
]

list_keys = list()


def gen_key() -> str:

    gen = lambda: "".join(
        [
            random.choice(
                list("123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM")
            )
            for x in range(4)
        ]
    )
    while True:
        key = gen()
        if key not in list_keys:
            list_keys.append(key)
            return key


UPDATE_CURRENT = gen_key()
CURRENT = gen_key()
LIST_ORDER = gen_key()
MORE_INFO = gen_key()
CANCEL_ALL_ORDERS = gen_key()
INCLUDE_TO_ALGORITHM = gen_key()
EXCLUDE_FROM_ALGORITHM = gen_key()
FUNCTIONS_SPOT = gen_key()
DELETE_MESSAGE = gen_key()
CHECK_CURRENT_ORDER_BOOK = gen_key()
CERTAIN_LIST_MY_SPOTS = gen_key()
CERTAIN_LIST_MY_NOTES = gen_key()
UNIQ_TEXT_IN_NOTES = gen_key()
LIST_UNIQ_TEXT_IN_NOTES = gen_key()
ACTION = gen_key()
BACK = gen_key()
ALGORITHM = gen_key()
NOTE = gen_key()
EDIT_NOTE = gen_key()
CLEAR_NOTE = gen_key()
LIST_NOTE = gen_key()
ID = gen_key()

del list_keys
