# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any

import freezegun
import pytest
from fastapi.testclient import TestClient
from mora import lora
from more_itertools import one

from tests.cases import assert_registrations_equal

userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

association_uuid = "c2153d5d-4a2b-492d-a18c-c498f7bb6221"
engagement_uuid = "d000591f-8705-4324-897a-075e3623f37b"
leave_uuid = "b807628c-030c-4f5f-a438-de41c1f26ba5"
manager_uuid = "05609702-977f-4869-9fb4-50ad74c6999a"
role_uuid = "1b20d0b9-96a0-42a6-b196-293bb86e62e8"


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "orgfunc_uuid,is_vacant",
    [
        (association_uuid, True),
        (engagement_uuid, False),
        (leave_uuid, False),
        (manager_uuid, True),
        (role_uuid, False),
    ],
)
@freezegun.freeze_time("2000-12-01")
async def test_terminate_employee(
    service_client: TestClient, orgfunc_uuid: str, is_vacant: bool
) -> None:
    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

    payload = {"vacate": True, "validity": {"to": "2000-12-01"}}

    # None of these should be activate at this point in time,
    # and should therefore remain unaffected by the termination request
    async def get_expected(id: str, is_vacant: bool) -> dict:
        o = await c.organisationfunktion.get(id)
        assert o is not None
        assert isinstance(o, dict)

        o.update(
            livscykluskode="Rettet",
            note="Afsluttet",
        )
        if is_vacant:
            del o["relationer"]["tilknyttedebrugere"][0]["uuid"]
        else:
            v = one(o["tilstande"]["organisationfunktiongyldighed"])
            v["gyldighed"] = "Inaktiv"

        return o

    expected_orgfunc = await get_expected(orgfunc_uuid, is_vacant)

    response = service_client.request(
        "POST",
        f"/service/e/{userid}/terminate",
        json=payload,
    )
    assert response.status_code == 200
    assert response.json() == userid

    actual_orgfunc = await c.organisationfunktion.get(orgfunc_uuid)

    assert_registrations_equal(expected_orgfunc, actual_orgfunc)


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "orgfunc_uuid",
    [
        association_uuid,
        engagement_uuid,
        leave_uuid,
        manager_uuid,
        role_uuid,
    ],
)
@freezegun.freeze_time("2000-12-01")
async def test_terminate_employee_vacatables_full(
    service_client: TestClient,
    orgfunc_uuid: str,
) -> None:
    """
    Ensure that organisationfunktions that can be vacated are
    terminated as well, when run with 'full'
    """
    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

    payload = {"vacate": False, "validity": {"to": "2000-12-01"}}

    async def get_expected(id: str) -> dict:
        o = await c.organisationfunktion.get(id)
        assert o is not None
        assert isinstance(o, dict)

        o.update(
            livscykluskode="Rettet",
            note="Afsluttet",
        )

        v = one(o["tilstande"]["organisationfunktiongyldighed"])
        v["gyldighed"] = "Inaktiv"

        return o

    expected_orgfunc = await get_expected(orgfunc_uuid)

    response = service_client.request(
        "POST",
        f"/service/e/{userid}/terminate",
        json=payload,
    )
    assert response.status_code == 200
    assert response.json() == userid

    actual_orgfunc = await c.organisationfunktion.get(orgfunc_uuid)

    assert_registrations_equal(expected_orgfunc, actual_orgfunc)


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "orgfunc,orgfunc_uuid,expected",
    [
        (
            "manager",
            manager_uuid,
            {
                "manager_level": {
                    "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                },
                "manager_type": {
                    "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                },
                "org_unit": {
                    "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                },
                "person": {
                    "uuid": userid,
                },
                "responsibility": [
                    {
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                    }
                ],
                "uuid": manager_uuid,
                "user_key": "be736ee5-5c44-4ed9-b4a4-15ffa19e2848",
                "validity": {
                    "from": "2017-01-01",
                    "to": "2017-11-30",
                },
            },
        ),
        (
            "association",
            association_uuid,
            {
                "association_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "dynamic_classes": [],
                "org_unit": {"uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "person": {"uuid": userid},
                "primary": None,
                "substitute": None,
                "user_key": "bvn",
                "uuid": association_uuid,
                "validity": {"from": "2017-01-01", "to": "2017-11-30"},
                "it": None,
                "job_function": None,
            },
        ),
    ],
)
@freezegun.freeze_time("2017-01-01", tz_offset=1)
async def test_terminate_via_user(
    service_client: TestClient,
    orgfunc: str,
    orgfunc_uuid: str,
    expected: dict[str, Any],
) -> None:
    # Check the POST request
    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

    payload = {"vacate": True, "validity": {"to": "2017-11-30"}}

    response = service_client.request(
        "POST", f"/service/e/{userid}/terminate", json=payload
    )
    assert response.status_code == 200
    assert response.json() == userid

    expected_orgfunc = {
        **(await c.organisationfunktion.get(orgfunc_uuid)),
        "note": "Afsluttet",
        "livscykluskode": "Rettet",
    }
    expected_orgfunc["relationer"]["tilknyttedebrugere"] = [
        {
            "uuid": userid,
            "virkning": {
                "from_included": True,
                "to_included": False,
                "from": "2017-01-01 00:00:00+01",
                "to": "2017-12-01 00:00:00+01",
            },
        },
        {
            "virkning": {
                "from_included": True,
                "to_included": False,
                "from": "2017-12-01 00:00:00+01",
                "to": "infinity",
            }
        },
    ]

    actual_orgfunc = await c.organisationfunktion.get(orgfunc_uuid)

    assert_registrations_equal(expected_orgfunc, actual_orgfunc)

    response = service_client.request(
        "GET",
        f"/service/e/{userid}/details/{orgfunc}",
        params={"only_primary_uuid": 1},
    )
    assert response.status_code == 200
    assert response.json() == [expected]

    response = service_client.request(
        "GET",
        f"/service/e/{userid}/details/{orgfunc}",
        params={"validity": "future", "only_primary_uuid": 1},
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            **expected,
            "person": None,
            "validity": {"from": "2017-12-01", "to": None},
        }
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "orgfunc_uuid",
    [
        engagement_uuid,
        association_uuid,
        manager_uuid,
        leave_uuid,
    ],
)
@freezegun.freeze_time("2017-01-01", tz_offset=1)
async def test_terminate_properly_via_user(
    service_client: TestClient,
    orgfunc_uuid: str,
) -> None:
    # Check the POST request
    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

    payload = {"vacate": False, "validity": {"to": "2017-11-30"}}

    response = service_client.request(
        "POST", f"/service/e/{userid}/terminate", json=payload
    )
    assert response.status_code == 200
    assert response.json() == userid

    expected_orgfunc = {
        **(await c.organisationfunktion.get(orgfunc_uuid)),
        "note": "Afsluttet",
        "livscykluskode": "Rettet",
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

    actual_orgfunc = await c.organisationfunktion.get(orgfunc_uuid)

    assert_registrations_equal(expected_orgfunc, actual_orgfunc)


@pytest.mark.integration_test
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
@freezegun.freeze_time("2017-01-01", tz_offset=1)
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
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2018-01-01")
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
