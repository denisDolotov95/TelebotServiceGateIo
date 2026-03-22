# -*- coding: utf-8 -*-
from fastapi import Request
from app import app


@app.get("/admin/{item_id}", tags=["Admin"])
def client_info(item_id: str, request: Request):

    client_host = request.client.host
    return {
        "client_host": client_host,
        "headers": request.headers.items(),
        "item_id": item_id,
    }
