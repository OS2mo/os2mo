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

from tests.conftest import test_app

# --------------------------------------------------------------------------------------
# Code
# --------------------------------------------------------------------------------------


@pytest.fixture(scope="class")
def graphapi_test():
    """Fixture yielding a FastAPI test client.

    This fixture is class scoped to ensure safe teardowns between test classes.
    """
    with TestClient(test_app(graphql_enable=True)) as client:
        yield client
