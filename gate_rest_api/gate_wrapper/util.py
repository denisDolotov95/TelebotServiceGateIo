# -*- coding: utf-8 -*-
import os
import json
import logging
import asyncio

from functools import wraps

from gate_api.exceptions import ApiException, GateApiException


def processing(*args, async_task=False, **kwargs):
    def decorator(func):
        if async_task:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                new_path = os.path.join("data", f"{func.__name__}.json")
                in_file = kwargs.get("in_file")
                if in_file:
                    del kwargs["in_file"]
                    with open(new_path, "w+"):
                        pass
                try:
                    result = await asyncio.to_thread(func, *args, **kwargs)
                    if in_file:
                        with open(new_path, "a+") as f:
                            json.dump(result, f)
                except GateApiException as err:
                    logging.error(
                        "Gate api exception, label: %s, message: %s\n"
                        % (err.label, err.message)
                    )
                    # if err.message.startswith("Invalid currency pair") or f"is delisted" in err.body:
                    #     return
                    return
                except ApiException as err:
                    logging.error(f"Exception when calling {func.__name__}: %s\n" % err)
                    return
                else:
                    return result

            return wrapper
        else:
            @wraps(func)
            def wrapper(*args, **kwargs):
                new_path = os.path.join("data", f"{func.__name__}.json")
                in_file = kwargs.get("in_file")
                if in_file:
                    del kwargs["in_file"]
                    with open(new_path, "w+"):
                        pass
                try:
                    data = func(*args, **kwargs)
                    if in_file:
                        with open(new_path, "a+") as f:
                            json.dump(data, f)
                except GateApiException as err:
                    logging.error(
                        "Gate api exception, label: %s, message: %s\n"
                        % (err.label, err.message)
                    )
                    # if err.message.startswith("Invalid currency pair") or f"is delisted" in err.body:
                    #     return
                    return
                except ApiException as err:
                    logging.error(f"Exception when calling {func.__name__}: %s\n" % err)
                    return
                else:
                    return data

            return wrapper

    return decorator
