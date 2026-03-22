import os
import pytest
import gate_api

from ..spot import Spot
from ..wallet import Wallet

__all__ = [
    "instance_spot",
    "instance_wallet",
]


GATE_CONFIGURATION = {
    "host": os.environ.get("GATE_HOST", "https://api.gateio.ws/api/v4"),
    "key": os.environ.get("GATE_KEY", "2c4ffa1c8b3f6a935b978e8a47a67e5f"),
    "secret": os.environ.get("GATE_SECRET", "ffa60f500082d0151e7df34fec035211033ea2c3dc423786b75f07603b85e9ab"),
}

if not GATE_CONFIGURATION["key"] or not GATE_CONFIGURATION["secret"]:
    pytest.skip(
        "Environment variables GATE_KEY and GATE_SECRET are not set; skipping Gate.io integration tests.",
        allow_module_level=True,
    )

api_client = gate_api.ApiClient(gate_api.Configuration(**GATE_CONFIGURATION))


@pytest.fixture(autouse=True, scope="class")
def instance_spot():
    spot = Spot(api_client)
    yield spot


@pytest.fixture(autouse=True, scope="class")
def instance_wallet():

    wallet = Wallet(api_client)
    yield wallet
