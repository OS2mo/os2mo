# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import os

import pytest
from fastapi.testclient import TestClient

from oio_rest.app import create_app


# Parts of the LoRa test suite assume that Keycloak authentication is turned on.
# We turn it on here before running the actual test suite.
os.environ["LORA_AUTH"] = "true"


@pytest.fixture(scope="session")
def lora_client() -> TestClient:
    app = create_app()
    client = TestClient(app)
    return client
