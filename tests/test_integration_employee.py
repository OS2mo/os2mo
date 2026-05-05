# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from uuid import UUID

import freezegun
import pytest
from fastapi.testclient import TestClient
from mora import lora
from mora.config import Settings
from more_itertools import one

from tests.cases import assert_registrations_equal

from . import util
from .conftest import AnotherTransaction


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
async def test_edit_employee_overwrite(service_client: TestClient) -> None:
    # A generic example of editing an employee

    userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

    req = [
        {
            "type": "employee",
            "original": {
                "validity": {"from": "2016-01-01 00:00:00+01", "to": None},
                "cpr_no": "1205320000",
                "givenname": "Fedtmule",
                "surname": "Hund",
                "uuid": userid,
            },
            "data": {
                "validity": {
                    "from": "2017-01-01",
                },
                "cpr_no": "0202020202",
                "givenname": "Test",
                "surname": "2 Employee",
                "nickname_givenname": "Testmand",
                "nickname_surname": "Whatever",
                "seniority": "2017-01-01",
            },
        }
    ]

    response = service_client.request("POST", "/service/details/edit", json=req)
    assert response.status_code == 200
    assert response.json() == [userid]

    # there must be a registration of the new name
    expected_brugeregenskaber = [
        {
            "brugervendtnoegle": "fedtmule",
            "virkning": {
                "from": "1932-05-12 00:00:00+01",
                "from_included": True,
                "to": "infinity",
                "to_included": False,
            },
        }
    ]

    expected_brugerudvidelser = [
        {
            "fornavn": "Fedtmule",
            "efternavn": "Hund",
            "kaldenavn_fornavn": "George",
            "kaldenavn_efternavn": "Geef",
            "virkning": {
                "from": "1932-05-12 00:00:00+01",
                "from_included": True,
                "to": "2017-01-01 00:00:00+01",
                "to_included": False,
            },
        },
        {
            "fornavn": "Test",
            "efternavn": "2 Employee",
            "kaldenavn_fornavn": "Testmand",
            "kaldenavn_efternavn": "Whatever",
            "seniority": "2017-01-01",
            "virkning": {
                "from": "2017-01-01 00:00:00+01",
                "from_included": True,
                "to": "infinity",
                "to_included": False,
            },
        },
    ]

    expected_tilknyttedepersoner = [
        {
            "urn": "urn:dk:cpr:person:0202020202",
            "virkning": {
                "from": "2017-01-01 00:00:00+01",
                "from_included": True,
                "to": "infinity",
                "to_included": False,
            },
        },
        {
            "urn": "urn:dk:cpr:person:1205320000",
            "virkning": {
                "from": "1932-05-12 00:00:00+01",
                "from_included": True,
                "to": "2017-01-01 00:00:00+01",
                "to_included": False,
            },
        },
    ]

    # but looking at the validity of the original that was sent along
    # the period from that fromdate up to the this fromdate has been
    # removed

    expected_brugergyldighed = [
        {
            "gyldighed": "Aktiv",
            "virkning": {
                "from": "1932-05-12 00:00:00+01",
                "from_included": True,
                "to": "2016-01-01 00:00:00+01",
                "to_included": False,
            },
        },
        {
            "gyldighed": "Aktiv",
            "virkning": {
                "from": "2017-01-01 00:00:00+01",
                "from_included": True,
                "to": "infinity",
                "to_included": False,
            },
        },
        {
            "gyldighed": "Inaktiv",
            "virkning": {
                "from": "2016-01-01 00:00:00+01",
                "from_included": True,
                "to": "2017-01-01 00:00:00+01",
                "to_included": False,
            },
        },
    ]

    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
    actual = await c.bruger.get(userid)
    assert actual is not None
    assert expected_brugeregenskaber == actual["attributter"]["brugeregenskaber"]
    assert expected_brugerudvidelser == actual["attributter"]["brugerudvidelser"]
    assert expected_brugergyldighed == actual["tilstande"]["brugergyldighed"]
    assert expected_tilknyttedepersoner == actual["relationer"]["tilknyttedepersoner"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
async def test_edit_remove_seniority(
    service_client: TestClient, another_transaction: AnotherTransaction
) -> None:
    # A generic example of editing an employee

    userid = "6ee24785-ee9a-4502-81c2-7697009c9053"
    async with another_transaction():
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
        actual = await c.bruger.get(userid)
        assert actual is not None

        actual_seniorities = [
            x.get("seniority", None) for x in actual["attributter"]["brugerudvidelser"]
        ]
        assert actual_seniorities == [None]

    req = [
        {
            "type": "employee",
            "original": None,
            "data": {
                "validity": {
                    "from": "2017-02-02",
                },
                "user_key": "regnbøfssalat",
                "seniority": "2017-01-01",
            },
            "uuid": userid,
        }
    ]

    response = service_client.request("POST", "/service/details/edit", json=req)
    assert response.status_code == 200
    assert response.json() == [userid]

    async with another_transaction():
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
        actual = await c.bruger.get(userid)
        assert actual is not None

        actual_seniorities = [
            x.get("seniority", None) for x in actual["attributter"]["brugerudvidelser"]
        ]
        assert actual_seniorities == ["2017-01-01", None]

    req = [
        {
            "type": "employee",
            "original": None,
            "data": {
                "validity": {
                    "from": "2017-02-03",
                },
                "seniority": None,
            },
            "uuid": userid,
        }
    ]

    response = service_client.request("POST", "/service/details/edit", json=req)
    assert response.status_code == 200
    assert response.json() == [userid]

    async with another_transaction():
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
        actual = await c.bruger.get(userid)
        assert actual is not None

        actual_seniorities = sorted(
            [
                x.get("seniority", None)
                for x in actual["attributter"]["brugerudvidelser"]
            ],
            key=(lambda x: ("" if (x is None) else x)),
        )
        assert actual_seniorities == [None, None, "2017-01-01"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "cpr_validate_birthdate,cpr,valid_from",
    [
        (True, "0101501234", "1950-01-01 00:00:00+01"),
        (False, "0101501234", "1950-01-01 00:00:00+01"),
        (False, "0171501234", "-infinity"),
    ],
)
@freezegun.freeze_time("2017-01-01", tz_offset=1)
async def test_create_employee(
    service_client: TestClient,
    cpr_validate_birthdate: bool,
    cpr: str,
    valid_from: str,
) -> None:
    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

    first_name = "Torkild"
    last_name = "von Testperson"

    payload = {
        "givenname": first_name,
        "surname": last_name,
        "nickname_givenname": "Torkild",
        "nickname_surname": "Sejfyr",
        "seniority": "2017-01-01",
        "cpr_no": cpr,
        "org": {"uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"},
    }

    with util.override_config(Settings(cpr_validate_birthdate=cpr_validate_birthdate)):
        response = service_client.request("POST", "/service/e/create", json=payload)
        assert response.status_code == 201
        userid = response.json()

    expected = _get_expected_response(first_name, last_name, cpr, valid_from)
    actual = await c.bruger.get(userid)
    assert actual is not None

    # Make sure the bvn is a valid UUID
    bvn = one(actual["attributter"]["brugeregenskaber"]).pop("brugervendtnoegle")
    assert UUID(bvn)

    assert_registrations_equal(expected, actual)

    response = service_client.request("GET", f"/service/e/{userid}/")
    assert response.status_code == 200
    assert response.json() == {
        "givenname": first_name,
        "surname": last_name,
        "name": f"{first_name} {last_name}",
        "nickname_givenname": "Torkild",
        "nickname_surname": "Sejfyr",
        "nickname": "Torkild Sejfyr",
        "seniority": "2017-01-01",
        "org": {
            "name": "Aarhus Universitet",
            "user_key": "AU",
            "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
        },
        "user_key": bvn,
        "uuid": userid,
        "cpr_no": cpr,
    }


def _get_expected_response(
    first_name: str, last_name: str, cpr: str, valid_from: str
) -> dict[str, Any]:
    expected = {
        "livscykluskode": "Importeret",
        "note": "Oprettet i MO",
        "attributter": {
            "brugeregenskaber": [
                {
                    "virkning": {
                        "to_included": False,
                        "to": "infinity",
                        "from_included": True,
                        "from": valid_from,
                    },
                }
            ],
            "brugerudvidelser": [
                {
                    "fornavn": first_name,
                    "efternavn": last_name,
                    "kaldenavn_fornavn": "Torkild",
                    "kaldenavn_efternavn": "Sejfyr",
                    "seniority": "2017-01-01",
                    "virkning": {
                        "from": valid_from,
                        "from_included": True,
                        "to": "infinity",
                        "to_included": False,
                    },
                }
            ],
        },
        "relationer": {
            "tilhoerer": [
                {
                    "virkning": {
                        "to_included": False,
                        "to": "infinity",
                        "from_included": True,
                        "from": valid_from,
                    },
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                }
            ],
        },
        "tilstande": {
            "brugergyldighed": [
                {
                    "virkning": {
                        "to_included": False,
                        "to": "infinity",
                        "from_included": True,
                        "from": valid_from,
                    },
                    "gyldighed": "Aktiv",
                }
            ]
        },
    }

    if cpr:
        tilknyttedepersoner = [
            {
                "virkning": {
                    "to_included": False,
                    "to": "infinity",
                    "from_included": True,
                    "from": valid_from,
                },
                "urn": "urn:dk:cpr:person:%s" % cpr,
            }
        ]
        expected["relationer"]["tilknyttedepersoner"] = tilknyttedepersoner

    return expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
async def test_edit_employee(service_client: TestClient) -> None:
    # A generic example of editing an employee

    userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

    req = [
        {
            "type": "employee",
            "original": None,
            "data": {
                "validity": {
                    "from": "2017-02-02",
                },
                "user_key": "regnbøfssalat",
                "cpr_no": "0101010101",
                "givenname": "Martin L",
                "surname": "Gore",
                "nickname_givenname": "John",
                "nickname_surname": "Morfar",
                "seniority": "2017-01-01",
            },
            "uuid": userid,
        }
    ]

    response = service_client.request("POST", "/service/details/edit", json=req)
    assert response.status_code == 200
    assert response.json() == [userid]

    # there must be a registration of the new name
    expected_brugeregenskaber = [
        {
            "brugervendtnoegle": "fedtmule",
            "virkning": {
                "from": "1932-05-12 00:00:00+01",
                "from_included": True,
                "to": "2017-02-02 00:00:00+01",
                "to_included": False,
            },
        },
        {
            "brugervendtnoegle": "regnbøfssalat",
            "virkning": {
                "from": "2017-02-02 00:00:00+01",
                "from_included": True,
                "to": "infinity",
                "to_included": False,
            },
        },
    ]

    expected_brugerudvidelser = [
        {
            "fornavn": "Fedtmule",
            "efternavn": "Hund",
            "kaldenavn_fornavn": "George",
            "kaldenavn_efternavn": "Geef",
            "virkning": {
                "from": "1932-05-12 00:00:00+01",
                "from_included": True,
                "to": "2017-02-02 00:00:00+01",
                "to_included": False,
            },
        },
        {
            "fornavn": "Martin L",
            "efternavn": "Gore",
            "kaldenavn_fornavn": "John",
            "kaldenavn_efternavn": "Morfar",
            "seniority": "2017-01-01",
            "virkning": {
                "from": "2017-02-02 00:00:00+01",
                "from_included": True,
                "to": "infinity",
                "to_included": False,
            },
        },
    ]

    # but looking at the validity of the original that was sent along
    # the period from that fromdate up to the this fromdate has been
    # removed

    expected_brugergyldighed = [
        {
            "gyldighed": "Aktiv",
            "virkning": {
                "from": "1932-05-12 00:00:00+01",
                "from_included": True,
                "to": "infinity",
                "to_included": False,
            },
        }
    ]

    expected_tilknyttedepersoner = [
        {
            "urn": "urn:dk:cpr:person:0101010101",
            "virkning": {
                "from": "2017-02-02 00:00:00+01",
                "from_included": True,
                "to": "infinity",
                "to_included": False,
            },
        },
        {
            "urn": "urn:dk:cpr:person:1205320000",
            "virkning": {
                "from": "1932-05-12 00:00:00+01",
                "from_included": True,
                "to": "2017-02-02 00:00:00+01",
                "to_included": False,
            },
        },
    ]

    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
    actual = await c.bruger.get(userid)
    assert actual is not None
    assert expected_brugeregenskaber == actual["attributter"]["brugeregenskaber"]
    assert expected_brugerudvidelser == actual["attributter"]["brugerudvidelser"]
    assert expected_brugergyldighed == actual["tilstande"]["brugergyldighed"]
    assert expected_tilknyttedepersoner == actual["relationer"]["tilknyttedepersoner"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
async def test_edit_employee_without_cpr(service_client: TestClient) -> None:
    # Add a cpr_no to an employee who doesn't have one

    userid = "4a53c06b-c1b5-417c-8c2e-bed526d34dbb"

    req = [
        {
            "type": "employee",
            "original": None,
            "data": {
                "validity": {
                    "from": "2017-02-02",
                },
                "user_key": "lol123",
                "cpr_no": "0101010101",
            },
            "uuid": userid,
        }
    ]

    response = service_client.request("POST", "/service/details/edit", json=req)
    assert response.status_code == 200
    assert response.json() == [userid]

    # there must be a registration of the new name
    expected_brugeregenskaber = [
        {
            "brugervendtnoegle": "lol123",
            "virkning": {
                "from": "2017-02-02 00:00:00+01",
                "from_included": True,
                "to": "infinity",
                "to_included": False,
            },
        },
        {
            "brugervendtnoegle": "mickeymouse",
            "virkning": {
                "from": "1932-05-12 00:00:00+01",
                "from_included": True,
                "to": "2017-02-02 00:00:00+01",
                "to_included": False,
            },
        },
    ]

    expected_tilknyttedepersoner = [
        {
            "urn": "urn:dk:cpr:person:0101010101",
            "virkning": {
                "from": "2017-02-02 00:00:00+01",
                "from_included": True,
                "to": "infinity",
                "to_included": False,
            },
        }
    ]

    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
    actual = await c.bruger.get(userid)
    assert actual is not None
    assert expected_brugeregenskaber == actual["attributter"]["brugeregenskaber"]
    assert expected_tilknyttedepersoner == actual["relationer"]["tilknyttedepersoner"]


userid = "ef78f929-2eb4-4d9e-8891-f9e8dcb47533"


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "payload,status_code,expected",
    [
        # Import
        (
            {
                "givenname": "Teodor",
                "surname": "Testfætter",
                "user_key": "testfætter",
                "org": {"uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"},
                "uuid": userid,
            },
            201,
            userid,
        ),
        # Empty payload
        (
            {},
            400,
            {
                "description": "Missing required value.",
                "error": True,
                "error_key": "V_MISSING_REQUIRED_VALUE",
                "name": "Missing name or givenname or surname",
                "status": 400,
            },
        ),
        # Invalid CPR
        (
            {
                "name": "Torkild Testperson",
                "cpr_no": "1",
                "org": {"uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"},
            },
            400,
            {
                "cpr": "1",
                "description": "Not a valid CPR number.",
                "error": True,
                "error_key": "V_CPR_NOT_VALID",
                "status": 400,
            },
        ),
        # Existing CPR
        (
            {
                "givenname": "Torkild",
                "surname": "Testperson",
                "cpr_no": "0906340000",
                "org": {"uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"},
            },
            409,
            {
                "description": "Person with CPR number already exists.",
                "error": True,
                "error_key": "V_EXISTING_CPR",
                "status": 409,
            },
        ),
        # Double naming
        (
            {
                "givenname": "Torkild",
                "surname": "Testperson",
                "name": "Torkild Testperson",
                "cpr_no": "0906340000",
                "org": {"uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"},
            },
            400,
            {
                "description": "Invalid input.",
                "error": True,
                "error_key": "E_INVALID_INPUT",
                "name": "Supply either name or given name/surame",
                "status": 400,
            },
        ),
        # Existing CPR different org
        (
            {
                "name": "Torkild Testperson",
                "cpr_no": "0906340000",
                "org": {"uuid": "3dcb1072-482e-491e-a8ad-647991d0bfcf"},
            },
            400,
            {
                "description": "Organisation is not allowed",
                "uuid": "3dcb1072-482e-491e-a8ad-647991d0bfcf",
                "status": 400,
                "error_key": "E_ORG_NOT_ALLOWED",
                "error": True,
            },
        ),
    ],
)
@freezegun.freeze_time("2017-01-01", tz_offset=1)
def test_create_employee_import_and_errors(
    service_client: TestClient, payload: dict, status_code: int, expected: Any
) -> None:
    """Test that creating an employee works as expected."""
    response = service_client.request("POST", "/service/e/create", json=payload)
    assert response.status_code == status_code
    assert response.json() == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_create_employee_with_details(service_client: TestClient) -> None:
    """Test creating an employee with added details.
    Also add three names to a single name parameter and check
    it will be split on lest space."""
    employee_uuid = "f7bcc7b1-381a-4f0e-a3f5-48a7b6eedf1c"

    payload = {
        "name": "Torkild Von Testperson",
        "cpr_no": "0101501234",
        "org": {"uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"},
        "details": [
            {
                "type": "engagement",
                "org_unit": {"uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "job_function": {"uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"},
                "engagement_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "validity": {
                    "from": "2016-12-01",
                    "to": None,
                },
            }
        ],
        "uuid": employee_uuid,
    }

    response = service_client.request("POST", "/service/e/create", json=payload)
    assert response.status_code == 201
    assert response.json() == employee_uuid

    response = service_client.request("GET", f"/service/e/{employee_uuid}/")
    assert response.status_code == 200
    assert response.json() == {
        "surname": "Testperson",
        "givenname": "Torkild Von",
        "name": "Torkild Von Testperson",
        "nickname_surname": "",
        "nickname_givenname": "",
        "seniority": None,
        "nickname": "",
        "org": {
            "name": "Aarhus Universitet",
            "user_key": "AU",
            "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
        },
        "user_key": employee_uuid,
        "cpr_no": "0101501234",
        "uuid": employee_uuid,
    }

    response = service_client.request(
        "GET", f"/service/e/{employee_uuid}/details/engagement"
    )
    assert response.status_code == 200
    assert len(response.json()) == 1, "One engagement should exist"


employee_uuid = "d2e1b69e-def1-41b1-b652-e704af02591c"


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "payload,expected",
    [
        # Broken engagement
        (
            {
                "name": "Torkild Testperson",
                "cpr_no": "0101501234",
                "org": {"uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"},
                "details": [
                    {
                        "type": "engagement",
                        "org_unit": {"uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                        "job_function": {
                            "uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"
                        },
                        "engagement_type": {
                            "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
                        },
                        "validity": {
                            "from": "1960-12-01",
                            "to": "2017-12-01",
                        },
                    }
                ],
                "uuid": employee_uuid,
            },
            {
                "description": "Date range exceeds validity "
                "range of associated org unit.",
                "error": True,
                "error_key": "V_DATE_OUTSIDE_ORG_UNIT_RANGE",
                "org_unit_uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                "status": 400,
                "valid_from": "2016-01-01",
                "valid_to": None,
            },
        ),
        # Broken employee
        (
            {
                "name": "Torkild Testperson",
                "cpr_no": "0101174234",
                "org": {"uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"},
                "details": [
                    {
                        "type": "engagement",
                        "org_unit": {"uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                        "job_function": {
                            "uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"
                        },
                        "engagement_type": {
                            "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
                        },
                        "validity": {
                            "from": "2016-12-01",
                            "to": "2017-12-01",
                        },
                    }
                ],
                "uuid": employee_uuid,
            },
            {
                "description": "Date range exceeds validity "
                "range of associated employee.",
                "error": True,
                "error_key": "V_DATE_OUTSIDE_EMPL_RANGE",
                "status": 400,
                "valid_from": "2017-01-01",
                "valid_to": "9999-12-31",
            },
        ),
    ],
)
def test_create_employee_with_details_fails_atomically(
    service_client: TestClient,
    payload: dict[str, Any],
    expected: dict[str, Any],
) -> None:
    """Ensure that we only save data when everything validates correctly"""

    response = service_client.request("POST", "/service/e/create", json=payload)
    assert response.status_code == 400
    assert response.json() == expected

    # Assert that nothing has been written
    response = service_client.request("GET", f"/service/e/{employee_uuid}/")
    assert response.status_code == 404
    assert response.json() == {
        "status": 404,
        "error": True,
        "description": "User not found.",
        "error_key": "E_USER_NOT_FOUND",
    }

    response = service_client.request(
        "GET", f"/service/e/{employee_uuid}/details/engagement"
    )
    assert response.status_code == 200
    assert response.json() == [], "No engagement should have been created"


@pytest.mark.parametrize(
    "cpr",
    [
        "1234/",
        "1234",
        "1234567890123",
    ],
)
def test_cpr_lookup_raises_on_wrong_length(
    service_client: TestClient,
    cpr: str,
) -> None:
    response = service_client.request(
        "GET",
        f"/service/e/cpr_lookup/?q={cpr}",
    )
    assert response.status_code == 400
    assert response.json() == {
        "cpr": cpr,
        "description": "Not a valid CPR number.",
        "error": True,
        "error_key": "V_CPR_NOT_VALID",
        "status": 400,
    }
