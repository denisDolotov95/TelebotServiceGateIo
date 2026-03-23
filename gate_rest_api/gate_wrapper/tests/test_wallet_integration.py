# -*- coding: utf-8 -*-
import pytest

from gate_wrapper.model import *


@pytest.mark.asyncio
@pytest.mark.usefixtures("wallet_instance")
class TestWallet:
    """Integration tests with service gate.io"""

    async def test_async_total_balance(self, wallet_instance):

        for async_req in {False, True}:
            response = await wallet_instance.total_balance(
                async_req=async_req, _request_timeout=(5, 5)
            )
            assert isinstance(response, TotalBalance)
