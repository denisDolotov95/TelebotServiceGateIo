# -*- coding: utf-8 -*-
import gate_api


# from datetime import datetime
from .util import processing
from .parse import ParseTotalBalance, TotalBalance

__all__ = ["Wallet"]


class Wallet:

    __async_to_thread = True

    def __init__(self, api_client: gate_api.ApiClient, instance: gate_api.WalletApi = None) -> None:

        self.wallet_api_instance = (
            instance if instance is not None else gate_api.WalletApi(api_client)
        )

    @processing(async_task=__async_to_thread)
    def total_balance(self, *args, **kwargs) -> TotalBalance:
        """https://www.gate.io/docs/developers/apiv4/en/#retrieve-personal-trading-fee

        Returns:
            TotalBalance: _description_
        """
        api_response = self.wallet_api_instance.get_total_balance(*args, **kwargs)
        return ParseTotalBalance(
            api_response.get().to_dict()
            if kwargs.get("async_req")
            else api_response.to_dict()
        ).parse()
