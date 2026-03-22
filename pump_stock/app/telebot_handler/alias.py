# -*- coding: utf-8 -*-
import random

__all__ = [
    "ACTION",
    "ALGORITHM",
    "BACK",
    "CANCEL_ALL_ORDERS",
    "CLEAR_NOTE",
    "CURRENT",
    "EDIT_NOTE",
    "ID",
    "CERTAIN_LIST_MY_NOTES",
    "UNIQ_TEXT_IN_NOTES",
    "LIST_UNIQ_TEXT_IN_NOTES",
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
ALGORITHM = gen_key()
ACTION = gen_key()
BACK = gen_key()
NOTE = gen_key()
EDIT_NOTE = gen_key()
CLEAR_NOTE = gen_key()
LIST_NOTE = gen_key()
UNIQ_TEXT_IN_NOTES = gen_key()
LIST_UNIQ_TEXT_IN_NOTES = gen_key()
CERTAIN_LIST_MY_NOTES = gen_key()
ID = gen_key()

del list_keys
