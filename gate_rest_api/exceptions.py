# -*- coding: utf-8 -*-
import gate_api

from fastapi import Request
from fastapi.responses import PlainTextResponse

from app import app

@app.exception_handler(gate_api.exceptions.OpenApiException)
async def global_exception_handler(request: Request, exc: gate_api.exceptions.OpenApiException):
    return PlainTextResponse(
        status_code=exc.status,
        content=str(exc),
    )