# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import AsyncIterator
from collections.abc import Callable
from uuid import UUID

import pytest
from aioresponses import aioresponses
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from os2mo_http_trigger_protocol import MOTriggerRegister

from mora import lora
from mora import mapping
from mora.config import Settings
from mora.handler.impl.association import AssociationReader
from mora.service.orgunit import UnitDetails
from mora.service.orgunit import get_one_orgunit
from mora.triggers.internal.http_trigger import register
from tests import util


@pytest.fixture
async def refresh_trigger_mock() -> AsyncIterator[aioresponses]:
    """A boundary-mocked external http-trigger with a refresh trigger registered.

    Registers a trigger just like `create_app` does it on start-up, but installs
    an `aioresponses` mock as the receiver, so we can mock the response from the
    external http-service, and discover how it was called.

    The mock is yielded so tests can add the trigger's response and inspect the
    request it received.
    """
    with aioresponses() as mock:
        mock.get(
            "http://whatever/triggers",
            payload=jsonable_encoder(
                [
                    MOTriggerRegister(
                        event_type=mapping.EventType.ON_BEFORE,
                        request_type=mapping.RequestType.REFRESH,
                        role_type="org_unit",
                        url="/triggers/ou/refresh",
                    )
                ]
            ),
        )
        # Register against this mock only. The app registers http-triggers on
        # start-up too, and this test builds two apps, so configuring the endpoint
        # globally would register the trigger once per app.
        await register(Settings(http_endpoints=["http://whatever"]))
        yield mock


@pytest.fixture
def trigger_payloads(refresh_trigger_mock: aioresponses) -> Callable[[str], list[dict]]:
    """Return the JSON bodies POSTed to `url`, as captured at the boundary."""

    def payloads(url: str) -> list[dict]:
        return [
            call.kwargs["json"]
            for (method, called_url), calls in refresh_trigger_mock.requests.items()
            for call in calls
            if method == "POST" and str(called_url) == url
        ]

    return payloads


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_returns_integration_error_on_wrong_status(
    create_org_unit: Callable[[str, UUID | None], UUID],
    service_client: TestClient,
    refresh_trigger_mock: aioresponses,
    trigger_payloads: Callable[[str], list[dict]],
) -> None:
    """A non-200 from the external http-trigger fails the refresh with an
    INTEGRATION_ERROR carrying the external service's `detail`."""
    unit_uuid = create_org_unit("Kolding Kommune")

    error_msg = "Something horrible happened"
    refresh_trigger_mock.post(
        "http://whatever/triggers/ou/refresh",
        status=400,
        payload={"detail": error_msg},
    )

    response = service_client.get(f"/service/ou/{unit_uuid}/refresh")

    assert response.status_code == 400
    result = response.json()
    assert "INTEGRATION_ERROR" in result["error_key"]
    assert error_msg in result["description"]

    (payload,) = trigger_payloads("http://whatever/triggers/ou/refresh")
    assert payload == {
        "request_type": mapping.RequestType.REFRESH,
        "request": {"uuid": str(unit_uuid)},
        "role_type": "org_unit",
        "event_type": mapping.EventType.ON_BEFORE,
        "uuid": str(unit_uuid),
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_returns_message_on_success(
    create_org_unit: Callable[[str, UUID | None], UUID],
    service_client: TestClient,
    refresh_trigger_mock: aioresponses,
    trigger_payloads: Callable[[str], list[dict]],
) -> None:
    """A 200 from the external http-trigger surfaces its response body in the
    refresh `message`."""
    unit_uuid = create_org_unit("Kolding Kommune")

    response_msg = "Something good happened"
    refresh_trigger_mock.post(
        "http://whatever/triggers/ou/refresh",
        status=200,
        payload=response_msg,
    )

    response = service_client.get(f"/service/ou/{unit_uuid}/refresh")

    assert response.status_code == 200
    assert response_msg in response.json()["message"].splitlines()

    (payload,) = trigger_payloads("http://whatever/triggers/ou/refresh")
    assert payload == {
        "request_type": mapping.RequestType.REFRESH,
        "request": {"uuid": str(unit_uuid)},
        "role_type": "org_unit",
        "event_type": mapping.EventType.ON_BEFORE,
        "uuid": str(unit_uuid),
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_returns_404_on_unknown_unit(
    service_client: TestClient,
) -> None:
    """Refreshing an org unit that does not exist returns 404."""
    response = service_client.get(
        "/service/ou/44c86c7a-cfe0-447e-9706-33821b5721a4/refresh"
    )
    assert response.status_code == 404
    result = response.json()
    assert "NOT_FOUND" in result["error_key"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@util.patch_query_args()
async def test_get_one_orgunit_with_association_count() -> None:
    _connector = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
    orgunit = await get_one_orgunit(
        _connector,
        "2874e1dc-85e6-4269-823a-e1125484dfd3",
        count_related={"association": AssociationReader},
    )
    assert orgunit is not None
    assert "association_count" in orgunit


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "details,expected_keys",
    [
        (
            UnitDetails.NCHILDREN,
            {"uuid", "name", "user_key", "validity", "child_count"},
        ),
        (UnitDetails.PATH, {"uuid", "name", "user_key", "validity", "location"}),
    ],
)
@util.patch_query_args()
async def test_details(details: UnitDetails, expected_keys: set[str]) -> None:
    _connector = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
    orgunit = await get_one_orgunit(
        _connector, "2874e1dc-85e6-4269-823a-e1125484dfd3", details=details
    )
    assert orgunit is not None
    assert set(orgunit.keys()) == expected_keys
