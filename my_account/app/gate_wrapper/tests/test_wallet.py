# -*- coding: utf-8 -*-
import pytest
import asyncio

from ..model import *


@pytest.mark.usefixtures("instance_wallet")
class TestWallet:
    """Integration tests with service gate.io"""

    event_loop = asyncio.new_event_loop()

    asyncio.set_event_loop(event_loop)

    def test_async_total_balance(self, instance_wallet):

        for async_req in {False, True}:
            response = self.event_loop.run_until_complete(
                instance_wallet.total_balance(async_req=async_req)
            )
            assert isinstance(response, TotalBalance)
