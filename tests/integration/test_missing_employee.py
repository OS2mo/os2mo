# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import logging
from uuid import UUID

import pytest
from fastapi.encoders import jsonable_encoder
from fastramqpi.events import Event
from httpx import AsyncClient


@pytest.mark.integration_test
@pytest.mark.usefixtures("test_client")
@pytest.mark.parametrize(
    "url,missing_uuid",
    [
        ("/mo2ldap/reconcile", "343202e5-697a-4993-8740-2766327e868a"),
        ("/mo2ldap/person", "f491c107-1e58-4721-a48a-09852233f20a"),
    ],
)
@pytest.mark.xfail(reason="The endpoint currently returns 500 instead of 200")
async def test_missing_employee_endpoints(
    test_client: AsyncClient,
    caplog: pytest.LogCaptureFixture,
    url: str,
    missing_uuid: str,
) -> None:
    """Ensure that endpoints do not get stuck on non-existent employees."""
    event = Event[UUID](subject=missing_uuid, priority=1)

    with caplog.at_level(logging.ERROR):
        response = await test_client.post(url, json=jsonable_encoder(event))
    assert response.status_code == 200
    assert f"Unable to lookup employee: {missing_uuid}" in caplog.text
    assert "Could not find MO employee, likely deleted or invalid event" in caplog.text
