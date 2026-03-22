# -*- coding: utf-8 -*-
import model as api_model

from app import app
from gate_wrapper import wallet, model as gate_model, create_instanse


@app.post(
    "/wallet/total_balance", tags=["Wallet"], response_model=gate_model.TotalBalance
)
async def total_balance(data: api_model.Security) -> gate_model.TotalBalance:

    return await create_instanse(wallet.Wallet, data.key, data.secret).total_balance()
