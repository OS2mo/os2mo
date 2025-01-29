# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import patch

import freezegun
import pytest
from fastapi.testclient import TestClient
from mora import lora

mock_uuid = "1eb680cd-d8ec-4fd2-8ca0-dce2d03f59a5"


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2018-01-01", tz_offset=1)
async def test_edit_leave_no_overwrite(service_client: TestClient) -> None:
    leave_uuid = "b807628c-030c-4f5f-a438-de41c1f26ba5"

    req = [
        {
            "type": "leave",
            "uuid": leave_uuid,
            "data": {
                "user_key": "koflagerske",
                "leave_type": {"uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2"},
                "engagement": {"uuid": "d3028e2e-1d7a-48c1-ae01-d4c64e64bbab"},
                "validity": {
                    "from": "2018-04-01",
                },
            },
        }
    ]

    response = service_client.request("POST", "/service/details/edit", json=req)
    # amqp_topics={"employee.leave.update": 1},
    assert response.status_code == 200
    assert response.json() == [leave_uuid]

    expected_leave = {
        "note": "Rediger orlov",
        "relationer": {
            "organisatoriskfunktionstype": [
                {
                    "uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2",
                    "virkning": {
                        "from_included": True,
                        "to_included": False,
                        "from": "2018-04-01 00:00:00+02",
                        "to": "infinity",
                    },
                },
                {
                    "uuid": "bf65769c-5227-49b4-97c5-642cfbe41aa1",
                    "virkning": {
                        "from_included": True,
                        "to_included": False,
                        "from": "2017-01-01 00:00:00+01",
                        "to": "2018-04-01 00:00:00+02",
                    },
                },
            ],
            "tilknyttedefunktioner": [
                {
                    "uuid": "d000591f-8705-4324-897a-075e3623f37b",
                    "virkning": {
                        "from": "2017-01-01 00:00:00+01",
                        "from_included": True,
                        "to": "2018-04-01 00:00:00+02",
                        "to_included": False,
                    },
                },
                {
                    "uuid": "d3028e2e-1d7a-48c1-ae01-d4c64e64bbab",
                    "virkning": {
                        "from": "2018-04-01 00:00:00+02",
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                },
            ],
            "tilknyttedeorganisationer": [
                {
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                    "virkning": {
                        "from_included": True,
                        "to_included": False,
                        "from": "2017-01-01 00:00:00+01",
                        "to": "infinity",
                    },
                }
            ],
            "tilknyttedebrugere": [
                {
                    "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                    "virkning": {
                        "from_included": True,
                        "to_included": False,
                        "from": "2017-01-01 00:00:00+01",
                        "to": "infinity",
                    },
                }
            ],
        },
        "livscykluskode": "Rettet",
        "tilstande": {
            "organisationfunktiongyldighed": [
                {
                    "gyldighed": "Aktiv",
                    "virkning": {
                        "from_included": True,
                        "to_included": False,
                        "from": "2017-01-01 00:00:00+01",
                        "to": "infinity",
                    },
                }
            ]
        },
        "attributter": {
            "organisationfunktionegenskaber": [
                {
                    "virkning": {
                        "from_included": True,
                        "to_included": False,
                        "from": "2017-01-01 00:00:00+01",
                        "to": "2018-04-01 00:00:00+02",
                    },
                    "brugervendtnoegle": "bvn",
                    "funktionsnavn": "Orlov",
                },
                {
                    "virkning": {
                        "from_included": True,
                        "to_included": False,
                        "from": "2018-04-01 00:00:00+02",
                        "to": "infinity",
                    },
                    "brugervendtnoegle": "koflagerske",
                    "funktionsnavn": "Orlov",
                },
            ]
        },
    }

    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
    actual_leave = await c.organisationfunktion.get(leave_uuid)

    # drop lora-generated timestamps & users
    del (
        actual_leave["fratidspunkt"],
        actual_leave["tiltidspunkt"],
        actual_leave["brugerref"],
    )

    assert expected_leave == actual_leave


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2018-01-01", tz_offset=1)
def test_create_leave(service_client: TestClient) -> None:
    # Check the POST request
    userid = "236e0a78-11a0-4ed9-8545-6286bb8611c7"
    leave_type = "62ec821f-4179-4758-bfdf-134529d186e9"
    engagement_uuid = "d000591f-8705-4324-897a-075e3623f37b"

    payload = [
        {
            "type": "leave",
            "person": {
                "uuid": userid,
            },
            "leave_type": {"uuid": leave_type},
            "engagement": {"uuid": engagement_uuid},
            "user_key": "1234",
            "validity": {
                "from": "2017-12-01",
                "to": None,
            },
        }
    ]

    expected = [
        {
            "engagement": {"uuid": "d3028e2e-1d7a-48c1-ae01-d4c64e64bbab"},
            "leave_type": {"uuid": "bf65769c-5227-49b4-97c5-642cfbe41aa1"},
            "person": {"uuid": "236e0a78-11a0-4ed9-8545-6286bb8611c7"},
            "user_key": "bvn",
            "uuid": "0895b7f5-86ac-45c5-8fb1-c3047d45b643",
            "validity": {"from": "2017-01-01", "to": None},
        },
        {
            "engagement": {"uuid": "d000591f-8705-4324-897a-075e3623f37b"},
            "leave_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
            "person": {"uuid": "236e0a78-11a0-4ed9-8545-6286bb8611c7"},
            "user_key": "1234",
            "uuid": mock_uuid,
            "validity": {"from": "2017-12-01", "to": None},
        },
    ]

    with patch("uuid.uuid4", new=lambda: mock_uuid):
        response = service_client.request(
            "POST", "/service/details/create", json=payload
        )
        # amqp_topics={"employee.leave.create": 1},
        assert response.status_code == 201

    response = service_client.request(
        "GET",
        f"/service/e/{userid}/details/leave?only_primary_uuid=1",
    )
    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2018-01-01", tz_offset=1)
def test_create_leave_fails_on_empty_payload(service_client: TestClient) -> None:
    payload = [
        {
            "type": "leave",
        }
    ]
    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == 400
    assert response.json() == {
        "description": "Missing person",
        "error": True,
        "error_key": "V_MISSING_REQUIRED_VALUE",
        "key": "person",
        "obj": payload[0],
        "status": 400,
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2018-01-01", tz_offset=1)
def test_create_leave_fails_when_no_active_engagement(
    service_client: TestClient,
) -> None:
    """Should fail on validation when the employee has no
    active engagements"""
    # Check the POST request
    userid = "6ee24785-ee9a-4502-81c2-7697009c9053"
    leave_type = "62ec821f-4179-4758-bfdf-134529d186e9"

    payload = [
        {
            "type": "leave",
            "person": {
                "uuid": userid,
            },
            "leave_type": {"uuid": leave_type},
            "validity": {
                "from": "2017-12-01",
                "to": "2017-12-01",
            },
        }
    ]

    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == 400
    assert response.json() == {
        "description": "Employee must have an active engagement.",
        "employee": "6ee24785-ee9a-4502-81c2-7697009c9053",
        "error": True,
        "error_key": "V_NO_ACTIVE_ENGAGEMENT",
        "status": 400,
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2018-01-01", tz_offset=1)
def test_edit_leave(service_client: TestClient) -> None:
    leave_uuid = "b807628c-030c-4f5f-a438-de41c1f26ba5"

    user_id = "236e0a78-11a0-4ed9-8545-6286bb8611c7"
    req = [
        {
            "type": "leave",
            "uuid": leave_uuid,
            "data": {
                "leave_type": {"uuid": "3c791935-2cfa-46b5-a12e-66f7f54e70fe"},
                "engagement": {"uuid": "301a906b-ef51-4d5c-9c77-386fb8410459"},
                "person": {"uuid": user_id},
                "user_key": "whatever",
                "validity": {
                    "from": "2017-01-01",
                },
            },
        }
    ]

    response = service_client.request("POST", "/service/details/edit", json=req)
    assert response.status_code == 200
    # amqp_topics={"employee.leave.update": 1},

    response = service_client.request(
        "GET", f"/service/e/{user_id}/details/leave?only_primary_uuid=1"
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            "uuid": "0895b7f5-86ac-45c5-8fb1-c3047d45b643",
            "user_key": "bvn",
            "validity": {"from": "2017-01-01", "to": None},
            "person": {"uuid": "236e0a78-11a0-4ed9-8545-6286bb8611c7"},
            "leave_type": {"uuid": "bf65769c-5227-49b4-97c5-642cfbe41aa1"},
            "engagement": {"uuid": "d3028e2e-1d7a-48c1-ae01-d4c64e64bbab"},
        },
        {
            "engagement": {"uuid": "301a906b-ef51-4d5c-9c77-386fb8410459"},
            "leave_type": {"uuid": "3c791935-2cfa-46b5-a12e-66f7f54e70fe"},
            "person": {"uuid": "236e0a78-11a0-4ed9-8545-6286bb8611c7"},
            "user_key": "whatever",
            "uuid": "b807628c-030c-4f5f-a438-de41c1f26ba5",
            "validity": {"from": "2017-01-01", "to": None},
        },
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2018-01-01", tz_offset=1)
def test_edit_leave_fails_when_no_active_engagement(service_client: TestClient) -> None:
    leave_uuid = "b807628c-030c-4f5f-a438-de41c1f26ba5"

    req = [
        {
            "type": "leave",
            "uuid": leave_uuid,
            "data": {
                "leave_type": {"uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2"},
                "validity": {
                    "from": "2016-04-01",
                    "to": "2016-04-01",
                },
            },
        }
    ]
    response = service_client.request("POST", "/service/details/edit", json=req)
    assert response.status_code == 400
    assert response.json() == {
        "description": "Employee must have an active engagement.",
        "employee": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
        "error": True,
        "error_key": "V_NO_ACTIVE_ENGAGEMENT",
        "status": 400,
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2018-01-01", tz_offset=1)
def test_terminate_leave(service_client: TestClient) -> None:
    userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

    payload = {"validity": {"to": "2017-11-30"}}

    response = service_client.request(
        "POST", f"/service/e/{userid}/terminate", json=payload
    )
    assert response.status_code == 200
    assert response.json() == userid
    #    amqp_topics={
    #        "employee.address.delete": 1,
    #        "employee.association.delete": 1,
    #        "employee.engagement.delete": 1,
    #        "employee.employee.delete": 1,
    #        "employee.it.delete": 1,
    #        "employee.leave.delete": 1,
    #        "employee.manager.delete": 1,
    #        "employee.role.delete": 1,
    #        "org_unit.association.delete": 1,
    #        "org_unit.engagement.delete": 1,
    #        "org_unit.manager.delete": 1,
    #        "org_unit.role.delete": 1,
    #    }

    response = service_client.request(
        "GET",
        f"/service/e/{userid}/details/leave?only_primary_uuid=1",
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2018-01-01", tz_offset=1)
def test_create_leave_missing_user(service_client: TestClient) -> None:
    # Check the POST request
    unitid = "da77153e-30f3-4dc2-a611-ee912a28d8aa"
    userid = "00000000-0000-0000-0000-000000000000"

    payload = [
        {
            "type": "leave",
            "person": {"uuid": userid},
            "org_unit": {"uuid": unitid},
            "leave_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
            "validity": {
                "from": "2017-12-01",
                "to": "2017-12-01",
            },
        }
    ]
    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == 404
    assert response.json() == {
        "description": "User not found.",
        "employee_uuid": "00000000-0000-0000-0000-000000000000",
        "error": True,
        "error_key": "E_USER_NOT_FOUND",
        "status": 404,
    }
