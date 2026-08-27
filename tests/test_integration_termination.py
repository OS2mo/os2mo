# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from fastapi.testclient import TestClient

from mora import lora
from tests.cases import assert_registrations_equal

userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

association_uuid = "c2153d5d-4a2b-492d-a18c-c498f7bb6221"
engagement_uuid = "d000591f-8705-4324-897a-075e3623f37b"
manager_uuid = "05609702-977f-4869-9fb4-50ad74c6999a"


@pytest.mark.integration_test
@pytest.mark.freeze_time("2017-01-01", tz_offset=1)
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "orgfunc,orgfunc_uuid",
    [
        ("association", association_uuid),
        ("engagement", engagement_uuid),
        # TODO: Figure out why leave cannot be terminated directly
        # ("leave", leave_uuid),
        ("manager", manager_uuid),
    ],
)
async def test_terminate_directly(
    service_client: TestClient,
    orgfunc: str,
    orgfunc_uuid: str,
) -> None:
    # Check the POST request
    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

    response = service_client.request("GET", f"/service/e/{userid}/details/{orgfunc}")
    assert response.status_code == 200
    original_orgfunc = response.json()

    response = service_client.request(
        "POST",
        "/service/details/terminate",
        json={
            "type": orgfunc,
            "uuid": orgfunc_uuid,
            "validity": {"to": "2017-11-30"},
        },
    )
    assert response.status_code == 200
    assert response.json() == orgfunc_uuid

    expected = {
        **(await c.organisationfunktion.get(orgfunc_uuid)),
        "livscykluskode": "Rettet",
        "note": "Afsluttet",
        "tilstande": {
            "organisationfunktiongyldighed": [
                {
                    "gyldighed": "Aktiv",
                    "virkning": {
                        "from_included": True,
                        "to_included": False,
                        "from": "2017-01-01 00:00:00+01",
                        "to": "2017-12-01 00:00:00+01",
                    },
                },
                {
                    "gyldighed": "Inaktiv",
                    "virkning": {
                        "from_included": True,
                        "to_included": False,
                        "from": "2017-12-01 00:00:00+01",
                        "to": "infinity",
                    },
                },
            ]
        },
    }

    # Create a new connector to clear the cache
    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

    actual = await c.organisationfunktion.get(orgfunc_uuid)

    assert_registrations_equal(expected, actual)

    # Current
    current = original_orgfunc
    current[0]["validity"]["to"] = "2017-11-30"

    response = service_client.request("GET", f"/service/e/{userid}/details/{orgfunc}")
    assert response.status_code == 200
    assert response.json() == current

    # Future
    response = service_client.request(
        "GET", f"/service/e/{userid}/details/{orgfunc}", params={"validity": "future"}
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "payload",
    [
        {
            "type": "manager",
            "uuid": manager_uuid,
        },
        {
            "type": "manager",
            "uuid": manager_uuid,
            "validity": {},
        },
        {
            "type": "manager",
            "uuid": manager_uuid,
            "validity": {
                "from": "2000-12-01",
            },
        },
    ],
)
def test_validation_missing_validity(service_client: TestClient, payload: dict) -> None:
    response = service_client.request(
        "POST", "/service/details/terminate", json=payload
    )
    assert response.status_code == 400
    assert response.json() == {
        "description": "Missing required value.",
        "error": True,
        "error_key": "V_MISSING_REQUIRED_VALUE",
        "key": "Validity must be set with either 'to' or both 'from' and 'to'",
        "obj": payload,
        "status": 400,
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_validation_missing_validity_invalid_type(service_client: TestClient) -> None:
    response = service_client.request(
        "POST",
        "/service/details/terminate",
        json={
            "type": "association",
            "uuid": manager_uuid,
            "validity": {
                "to": "2018-01-01",
            },
        },
    )
    assert response.status_code == 404


@pytest.mark.integration_test
@pytest.mark.freeze_time("2018-01-01")
@pytest.mark.usefixtures("fixture_db")
def test_validation_allow_to_equal_none(service_client: TestClient) -> None:
    response = service_client.request(
        "POST",
        "/service/details/terminate",
        json={
            "type": "address",
            "uuid": manager_uuid,
            "validity": {"from": "2000-12-01", "to": None},
        },
    )
    assert response.status_code == 200
    assert response.json() == manager_uuid
