# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests for mora.triggers.internal.http_trigger."""

import pytest
from aioresponses import aioresponses
from fastapi.encoders import jsonable_encoder
from os2mo_http_trigger_protocol import MOTriggerRegister

from mora import mapping
from mora.config import Settings
from mora.triggers import Trigger
from mora.triggers.internal.http_trigger import fetch_endpoint_triggers
from mora.triggers.internal.http_trigger import register


@pytest.fixture(autouse=True)
def reset_trigger_registry():
    """Isolate each test from triggers registered by other tests."""
    original = Trigger.registry
    Trigger.registry = {}
    try:
        yield
    finally:
        Trigger.registry = original


async def test_register_no_endpoints() -> None:
    """With no configured endpoints, register returns False without registering."""
    result = await register(Settings(http_endpoints=[]))
    assert result is False
    assert Trigger.registry == {}


async def test_register_with_endpoint() -> None:
    """With a configured endpoint, register fetches triggers and registers them."""
    trigger_register = MOTriggerRegister(
        event_type=mapping.EventType.ON_BEFORE,
        request_type=mapping.RequestType.CREATE,
        role_type="org_unit",
        url="/triggers/ou/refresh",
    )
    with aioresponses() as mock:
        mock.get(
            "http://whatever/triggers",
            payload=jsonable_encoder([trigger_register]),
        )
        result = await register(Settings(http_endpoints=["http://whatever"]))

    assert result is True
    assert "org_unit" in Trigger.registry
    assert mapping.RequestType.CREATE in Trigger.registry["org_unit"]
    assert (
        mapping.EventType.ON_BEFORE
        in Trigger.registry["org_unit"][mapping.RequestType.CREATE]
    )
    # One trigger function was registered
    assert (
        len(
            Trigger.registry["org_unit"][mapping.RequestType.CREATE][
                mapping.EventType.ON_BEFORE
            ]
        )
        == 1
    )


async def test_fetch_endpoint_triggers_success() -> None:
    """fetch_endpoint_triggers returns the parsed trigger configuration."""
    trigger_register = MOTriggerRegister(
        event_type=mapping.EventType.ON_BEFORE,
        request_type=mapping.RequestType.CREATE,
        role_type="org_unit",
        url="/triggers/ou/refresh",
    )
    with aioresponses() as mock:
        mock.get(
            "http://good/triggers",
            payload=jsonable_encoder([trigger_register]),
        )
        result = await fetch_endpoint_triggers(["http://good"])

    assert result == {"http://good": [trigger_register]}
