#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import pytest
from fastapi.testclient import TestClient

from mora.app import create_app
from mora.auth.keycloak.oidc import auth
from tests.cases import fake_auth

# --------------------------------------------------------------------------------------
# Code
# --------------------------------------------------------------------------------------


def test_app():
    app = create_app()
    app.dependency_overrides[auth] = fake_auth
    return app


@pytest.fixture(scope="class")
def serviceapi_test():
    """Fixture yielding a FastAPI test client.

    This fixture is class scoped to ensure safe teardowns between test classes.
    """
    yield TestClient(test_app())
