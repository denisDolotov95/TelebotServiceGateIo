# -*- coding: utf-8 -*-
import asyncio
import telebot

# from ..runners import analyse


class TestRunners:

    pass
    # event_loop = asyncio.new_event_loop()

    # asyncio.set_event_loop(event_loop)

    # def test_async_analyse(self):

    #     example = [{"currency": "MTA", "available": "0.0040018", "locked": "140.52"}]
    #     response = self.event_loop.run_until_complete(analyse(accounts=example))
    #     assert isinstance(response, list)
    #     for data in response:
    #         assert isinstance(data, dict)
    #         assert data.get("info") is not None
    #         assert data.get("keyboard") is not None
    #         assert isinstance(data.get("info"), str)
    #         assert isinstance(data.get("keyboard"), telebot.types.InlineKeyboardMarkup)