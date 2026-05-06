# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from operator import itemgetter

import freezegun
import pytest
from fastapi.testclient import TestClient

from . import util

org_unit_type_facet = {
    "description": "",
    "user_key": "org_unit_type",
    "uuid": "fc917e7c-fc3b-47c2-8aa5-a0383342a280",
}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
async def test_employee_empty_db(service_client: TestClient) -> None:
    # empty
    response = service_client.request(
        "GET",
        "/service/o/00000000-0000-0000-0000-000000000000/e/",
    )
    assert response.status_code == 200
    assert response.json() == {"total": 0, "items": [], "offset": 0}

    response = service_client.request(
        "GET",
        "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/",
    )
    assert response.status_code == 200
    assert response.json() == {"total": 0, "items": [], "offset": 0}


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
async def test_employee(another_transaction, service_client: TestClient) -> None:
    # invalid
    response = service_client.request(
        "GET",
        "/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a/?at=1920-01-01T00:00:00Z",
    )
    assert response.status_code == 404

    result = {
        "items": [
            {
                "cpr_no": "0910810000",
                "givenname": "Erik Smidt",
                "name": "Erik Smidt Hansen",
                "nickname": "",
                "nickname_givenname": "",
                "nickname_surname": "",
                "seniority": None,
                "org": {
                    "name": "Aarhus Universitet",
                    "user_key": "AU",
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                },
                "surname": "Hansen",
                "user_key": "eriksmidthansen",
                "uuid": "236e0a78-11a0-4ed9-8545-6286bb8611c7",
            },
            {
                "givenname": "Mickey",
                "name": "Mickey Mouse",
                "nickname": "",
                "nickname_givenname": "",
                "nickname_surname": "",
                "seniority": None,
                "org": {
                    "name": "Aarhus Universitet",
                    "user_key": "AU",
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                },
                "surname": "Mouse",
                "user_key": "mickeymouse",
                "uuid": "4a53c06b-c1b5-417c-8c2e-bed526d34dbb",
            },
            {
                "cpr_no": "0906340000",
                "givenname": "Anders",
                "name": "Anders And",
                "nickname": "Donald Duck",
                "nickname_givenname": "Donald",
                "nickname_surname": "Duck",
                "seniority": None,
                "org": {
                    "name": "Aarhus Universitet",
                    "user_key": "AU",
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                },
                "surname": "And",
                "user_key": "andersand",
                "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            },
            {
                "cpr_no": "1205320000",
                "givenname": "Fedtmule",
                "name": "Fedtmule Hund",
                "nickname": "George Geef",
                "nickname_givenname": "George",
                "nickname_surname": "Geef",
                "seniority": None,
                "org": {
                    "name": "Aarhus Universitet",
                    "user_key": "AU",
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                },
                "surname": "Hund",
                "user_key": "fedtmule",
                "uuid": "6ee24785-ee9a-4502-81c2-7697009c9053",
            },
            {
                "cpr_no": "0906730000",
                "givenname": "Lis",
                "name": "Lis Jensen",
                "nickname": "",
                "nickname_givenname": "",
                "nickname_surname": "",
                "seniority": None,
                "org": {
                    "name": "Aarhus Universitet",
                    "user_key": "AU",
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                },
                "surname": "Jensen",
                "user_key": "",
                "uuid": "7626ad64-327d-481f-8b32-36c78eb12f8c",
            },
        ],
        "offset": 0,
        "total": 5,
    }

    response = service_client.request(
        "GET", "/service/o/00000000-0000-0000-0000-000000000000/e/"
    )
    assert response.status_code == 200
    assert response.json() == result

    response = service_client.request(
        "GET", "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/"
    )
    assert response.status_code == 200
    assert response.json() == result

    response = service_client.request(
        "GET",
        "/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a/",
    )
    assert response.status_code == 200
    assert response.json() == {
        "name": "Anders And",
        "givenname": "Anders",
        "surname": "And",
        "nickname": "Donald Duck",
        "nickname_givenname": "Donald",
        "nickname_surname": "Duck",
        "seniority": None,
        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
        "user_key": "andersand",
        "cpr_no": "0906340000",
        "org": {
            "name": "Aarhus Universitet",
            "user_key": "AU",
            "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
        },
    }

    response = service_client.request(
        "GET",
        "/service/e/6ee24785-ee9a-4502-81c2-7697009c9053/",
    )
    assert response.status_code == 200
    assert response.json() == {
        "name": "Fedtmule Hund",
        "givenname": "Fedtmule",
        "surname": "Hund",
        "nickname": "George Geef",
        "nickname_givenname": "George",
        "nickname_surname": "Geef",
        "seniority": None,
        "uuid": "6ee24785-ee9a-4502-81c2-7697009c9053",
        "user_key": "fedtmule",
        "cpr_no": "1205320000",
        "org": {
            "name": "Aarhus Universitet",
            "user_key": "AU",
            "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
        },
    }

    with freezegun.freeze_time("1900-01-01"):
        response = service_client.request(
            "GET",
            "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/",
        )
        assert response.status_code == 200
        assert response.json() == {"total": 0, "items": [], "offset": 0}

    response = service_client.request(
        "GET",
        "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/?at=1900-01-01",
    )
    assert response.status_code == 200
    assert response.json() == {"total": 0, "items": [], "offset": 0}

    async with another_transaction():
        await util.load_fixture(
            "organisation/bruger",
            "create_bruger_andersine.json",
            "df55a3ad-b996-4ae0-b6ea-a3241c4cbb24",
        )

    result_list = [
        {
            "cpr_no": "0910810000",
            "givenname": "Erik Smidt",
            "name": "Erik Smidt Hansen",
            "nickname": "",
            "nickname_givenname": "",
            "nickname_surname": "",
            "seniority": None,
            "org": {
                "name": "Aarhus Universitet",
                "user_key": "AU",
                "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
            },
            "surname": "Hansen",
            "user_key": "eriksmidthansen",
            "uuid": "236e0a78-11a0-4ed9-8545-6286bb8611c7",
        },
        {
            "givenname": "Mickey",
            "name": "Mickey Mouse",
            "nickname": "",
            "nickname_givenname": "",
            "nickname_surname": "",
            "seniority": None,
            "org": {
                "name": "Aarhus Universitet",
                "user_key": "AU",
                "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
            },
            "surname": "Mouse",
            "user_key": "mickeymouse",
            "uuid": "4a53c06b-c1b5-417c-8c2e-bed526d34dbb",
        },
        {
            "cpr_no": "0906340000",
            "givenname": "Anders",
            "name": "Anders And",
            "nickname": "Donald Duck",
            "nickname_givenname": "Donald",
            "nickname_surname": "Duck",
            "seniority": None,
            "org": {
                "name": "Aarhus Universitet",
                "user_key": "AU",
                "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
            },
            "surname": "And",
            "user_key": "andersand",
            "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
        },
        {
            "cpr_no": "1205320000",
            "givenname": "Fedtmule",
            "name": "Fedtmule Hund",
            "nickname": "George Geef",
            "nickname_givenname": "George",
            "nickname_surname": "Geef",
            "seniority": None,
            "org": {
                "name": "Aarhus Universitet",
                "user_key": "AU",
                "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
            },
            "surname": "Hund",
            "user_key": "fedtmule",
            "uuid": "6ee24785-ee9a-4502-81c2-7697009c9053",
        },
        {
            "cpr_no": "0906730000",
            "givenname": "Lis",
            "name": "Lis Jensen",
            "nickname": "",
            "nickname_givenname": "",
            "nickname_surname": "",
            "seniority": None,
            "org": {
                "name": "Aarhus Universitet",
                "user_key": "AU",
                "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
            },
            "surname": "Jensen",
            "user_key": "",
            "uuid": "7626ad64-327d-481f-8b32-36c78eb12f8c",
        },
        {
            "cpr_no": "0901370000",
            "givenname": "Andersine",
            "name": "Andersine And",
            "nickname": "Daisy Duck",
            "nickname_givenname": "Daisy",
            "nickname_surname": "Duck",
            "seniority": None,
            "org": {
                "name": "Aarhus Universitet",
                "user_key": "AU",
                "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
            },
            "surname": "And",
            "user_key": "andersineand",
            "uuid": "df55a3ad-b996-4ae0-b6ea-a3241c4cbb24",
        },
    ]

    response = service_client.request(
        "GET",
        "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/",
    )
    assert response.status_code == 200
    assert response.json() == {"items": result_list, "offset": 0, "total": 6}

    response = service_client.request(
        "GET",
        "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/?limit=1",
    )
    assert response.status_code == 200
    assert response.json() == {"items": result_list[:1], "offset": 0, "total": 6}

    response = service_client.request(
        "GET",
        "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/?limit=1&start=1",
    )
    assert response.status_code == 200
    assert response.json() == {"items": result_list[1:][:1], "offset": 1, "total": 6}

    response = service_client.request(
        "GET",
        "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/?at=1937-01-01",
    )
    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "givenname": "Mickey",
                "name": "Mickey Mouse",
                "nickname": "",
                "nickname_givenname": "",
                "nickname_surname": "",
                "seniority": None,
                "org": {
                    "name": "Aarhus Universitet",
                    "user_key": "AU",
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                },
                "surname": "Mouse",
                "user_key": "mickeymouse",
                "uuid": "4a53c06b-c1b5-417c-8c2e-bed526d34dbb",
            },
            {
                "cpr_no": "0906340000",
                "givenname": "Anders",
                "name": "Anders And",
                "nickname": "Donald Duck",
                "nickname_givenname": "Donald",
                "nickname_surname": "Duck",
                "seniority": None,
                "org": {
                    "name": "Aarhus Universitet",
                    "user_key": "AU",
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                },
                "surname": "And",
                "user_key": "andersand",
                "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            },
            {
                "cpr_no": "1205320000",
                "givenname": "Fedtmule",
                "name": "Fedtmule Hund",
                "nickname": "George Geef",
                "nickname_givenname": "George",
                "nickname_surname": "Geef",
                "seniority": None,
                "org": {
                    "name": "Aarhus Universitet",
                    "user_key": "AU",
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                },
                "surname": "Hund",
                "user_key": "fedtmule",
                "uuid": "6ee24785-ee9a-4502-81c2-7697009c9053",
            },
        ],
        "offset": 0,
        "total": 3,
    }

    response = service_client.request(
        "GET",
        "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/?query=Anders",
    )
    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "cpr_no": "0906340000",
                "givenname": "Anders",
                "name": "Anders And",
                "nickname": "Donald Duck",
                "nickname_givenname": "Donald",
                "nickname_surname": "Duck",
                "seniority": None,
                "org": {
                    "name": "Aarhus Universitet",
                    "user_key": "AU",
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                },
                "surname": "And",
                "user_key": "andersand",
                "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            },
            {
                "cpr_no": "0901370000",
                "givenname": "Andersine",
                "name": "Andersine And",
                "nickname": "Daisy Duck",
                "nickname_givenname": "Daisy",
                "nickname_surname": "Duck",
                "seniority": None,
                "org": {
                    "name": "Aarhus Universitet",
                    "user_key": "AU",
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                },
                "surname": "And",
                "user_key": "andersineand",
                "uuid": "df55a3ad-b996-4ae0-b6ea-a3241c4cbb24",
            },
        ],
        "offset": 0,
        "total": 2,
    }

    response = service_client.request(
        "GET",
        "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/?at=1937-01-01&query=Anders",
    )
    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "cpr_no": "0906340000",
                "givenname": "Anders",
                "name": "Anders And",
                "nickname": "Donald Duck",
                "nickname_givenname": "Donald",
                "nickname_surname": "Duck",
                "seniority": None,
                "org": {
                    "name": "Aarhus Universitet",
                    "user_key": "AU",
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                },
                "surname": "And",
                "user_key": "andersand",
                "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            }
        ],
        "offset": 0,
        "total": 1,
    }

    # allow searching by cpr number
    response = service_client.request(
        "GET",
        "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/?query=0906340000",
    )
    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "cpr_no": "0906340000",
                "givenname": "Anders",
                "name": "Anders And",
                "nickname": "Donald Duck",
                "nickname_givenname": "Donald",
                "nickname_surname": "Duck",
                "seniority": None,
                "org": {
                    "name": "Aarhus Universitet",
                    "user_key": "AU",
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                },
                "surname": "And",
                "user_key": "andersand",
                "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            }
        ],
        "offset": 0,
        "total": 1,
    }

    # disallow partial matches for CPR numbers
    response = service_client.request(
        "GET",
        "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/?query=090634",
    )
    assert response.status_code == 200
    assert response.json() == {"items": [], "offset": 0, "total": 0}

    response = service_client.request(
        "GET",
        "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/?query=1",
    )
    assert response.status_code == 200
    assert response.json() == {"items": [], "offset": 0, "total": 0}

    # bogus
    response = service_client.request(
        "GET",
        "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/?query=0000000000",
    )
    assert response.status_code == 200
    assert response.json() == {"items": [], "offset": 0, "total": 0}

    response = service_client.request(
        "GET",
        "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/?query=Anders&associated=true",
    )
    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "cpr_no": "0906340000",
                "givenname": "Anders",
                "name": "Anders And",
                "nickname": "Donald Duck",
                "nickname_givenname": "Donald",
                "nickname_surname": "Duck",
                "seniority": None,
                "org": {
                    "name": "Aarhus Universitet",
                    "user_key": "AU",
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                },
                "surname": "And",
                "user_key": "andersand",
                "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            }
        ],
        "offset": 0,
        "total": 1,
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_children(service_client: TestClient) -> None:
    response = service_client.request(
        "GET", "/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/children"
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            "name": "Social og sundhed",
            "user_key": "social-sundhed",
            "uuid": "68c5d78e-ae26-441f-a143-0103eca8b62a",
            "validity": {"from": "2017-01-01", "to": None},
            "child_count": 0,
        },
        {
            "name": "Humanistisk fakultet",
            "user_key": "hum",
            "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            "validity": {
                "from": "2016-12-31",
                "to": None,
            },
            "child_count": 1,
        },
        {
            "name": "Samfundsvidenskabelige fakultet",
            "user_key": "samf",
            "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
            "validity": {
                "from": "2017-01-01",
                "to": None,
            },
            "child_count": 0,
        },
        {
            "name": "Skole og Børn",
            "user_key": "skole-børn",
            "uuid": "dad7d0ad-c7a9-4a94-969d-464337e31fec",
            "validity": {"from": "2017-01-01", "to": None},
            "child_count": 1,
        },
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_facet_create_and_update(service_client: TestClient) -> None:
    # Tests new creation - 200 message
    response = service_client.request(
        "POST",
        "/service/f/engagement_job_function/",
        json={
            "uuid": "18638313-d9e6-4e1d-aea6-67f5fce7a6b0",
            "user_key": "BVN",
            "name": "Jurist",
            "owner": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            "scope": "TEXT",
            "org_uuid": "0b6c3ae7-dfe9-4136-89ee-53de96fb688b",
        },
    )
    assert response.status_code == 200
    actual_post = response.json()
    assert actual_post == "18638313-d9e6-4e1d-aea6-67f5fce7a6b0"

    job_functions = [
        {
            "example": None,
            "name": "Skolepsykolog",
            "owner": None,
            "scope": None,
            "user_key": "Skolepsykolog",
            "uuid": "07cea156-1aaf-4c89-bf1b-8e721f704e22",
        },
        {
            "example": None,
            "name": "Specialist",
            "owner": None,
            "scope": "TEXT",
            "user_key": "specialist",
            "uuid": "890d4ff0-b453-4900-b79b-dbb461eda3ee",
        },
        {
            "example": None,
            "name": "Bogopsætter",
            "owner": None,
            "scope": None,
            "user_key": "Bogopsætter",
            "uuid": "f42dd694-f1fd-42a6-8a97-38777b73adc4",
        },
    ]

    # Tests the GET data matches
    response = service_client.request("GET", "/service/f/engagement_job_function/")
    assert response.status_code == 200
    actual_get = response.json()
    assert actual_get == {
        "uuid": "1a6045a2-7a8e-4916-ab27-b2402e64f2be",
        "user_key": "engagement_job_function",
        "description": "",
        "data": {
            "total": 4,
            "offset": 0,
            "items": sorted(
                job_functions
                + [
                    {
                        "example": None,
                        "name": "Jurist",
                        "owner": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "scope": "TEXT",
                        "user_key": "BVN",
                        "uuid": "18638313-d9e6-4e1d-aea6-67f5fce7a6b0",
                    }
                ],
                key=itemgetter("uuid"),
            ),
        },
    }

    # Tests PUT on the same class
    response = service_client.request(
        "POST",
        "/service/f/engagement_job_function/",
        # Updated payload, same uuid
        json={
            "uuid": "18638313-d9e6-4e1d-aea6-67f5fce7a6b0",
            "facet_uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "user_key": "BVN",
            "name": "Ergoterapeut",
            "scope": "TEXT",
            "org_uuid": "0b6c3ae7-dfe9-4136-89ee-53de96fb688b",
        },
    )
    assert response.status_code == 200
    actual_put = response.json()
    assert actual_put == "18638313-d9e6-4e1d-aea6-67f5fce7a6b0"

    # Tests the GET data matches
    response = service_client.request("GET", "/service/f/engagement_job_function/")
    assert response.status_code == 200
    actual_get = response.json()
    assert actual_get == {
        "uuid": "1a6045a2-7a8e-4916-ab27-b2402e64f2be",
        "user_key": "engagement_job_function",
        "description": "",
        "data": {
            "total": 4,
            "offset": 0,
            "items": sorted(
                job_functions
                + [
                    {
                        "example": None,
                        "name": "Ergoterapeut",
                        "owner": None,
                        "scope": "TEXT",
                        "user_key": "BVN",
                        "uuid": "18638313-d9e6-4e1d-aea6-67f5fce7a6b0",
                    }
                ],
                key=itemgetter("uuid"),
            ),
        },
    }


@freezegun.freeze_time("2017-01-01", tz_offset=1)
@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "params,expected",
    [
        ({}, lambda result_list: {"items": result_list, "offset": 0, "total": 12}),
        # list with a limit
        (
            {"limit": "2"},
            lambda result_list: {
                "items": result_list[:2],
                "offset": 0,
                "total": 12,
            },
        ),
        # list with a limit and a start
        (
            {"limit": "3", "start": "1"},
            lambda result_list: {
                "items": result_list[1:][:3],
                "offset": 1,
                "total": 12,
            },
        ),
        # paging
        (
            {"limit": "3"},
            lambda result_list: {
                "items": result_list[:3],
                "offset": 0,
                "total": 12,
            },
        ),
        (
            {"limit": "3", "start": "3"},
            lambda result_list: {
                "items": result_list[3:][:3],
                "offset": 3,
                "total": 12,
            },
        ),
        # searching
        (
            {"query": "frem"},
            lambda _: {
                "items": [
                    {
                        "name": "Afdeling for Samtidshistorik",
                        "user_key": "frem",
                        "uuid": "04c78fc2-72d2-4d02-b55f-807af19eac48",
                        "validity": {
                            "from": "2016-01-01",
                            "to": "2018-12-31",
                        },
                    }
                ],
                "offset": 0,
                "total": 1,
            },
        ),
        (
            {"query": "over"},
            lambda _: {
                "items": [
                    {
                        "name": "Overordnet Enhed",
                        "user_key": "root",
                        "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                        "validity": {
                            "from": "2016-01-01",
                            "to": None,
                        },
                    }
                ],
                "offset": 0,
                "total": 1,
            },
        ),
        (
            {"query": "over", "root": "2874e1dc-85e6-4269-823a-e1125484dfd3"},
            lambda _: {
                "items": [
                    {
                        "name": "Overordnet Enhed",
                        "user_key": "root",
                        "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                        "validity": {
                            "from": "2016-01-01",
                            "to": None,
                        },
                    }
                ],
                "offset": 0,
                "total": 1,
            },
        ),
        (
            {"query": "over", "root": "deadbeef-cafe-babe-f00d-decafbadfood"},
            lambda _: {"items": [], "offset": 0, "total": 0},
        ),
        # search and return paths
        # When requesting with "details=path", the result should include a "location"
        # for each matching org unit
        (
            {"query": "samf", "details": "path"},
            lambda _: {
                "items": [
                    {
                        "location": "Overordnet Enhed",
                        "name": "Samfundsvidenskabelige fakultet",
                        "user_key": "samf",
                        "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
                        "validity": {"from": "2017-01-01", "to": None},
                    }
                ],
                "offset": 0,
                "total": 1,
            },
        ),
    ],
)
def test_orgunit_search(
    service_client: TestClient,
    params: dict[str, str],
    expected: Callable,
) -> None:
    result_list = [
        {
            "user_key": "frem",
            "name": "Afdeling for Samtidshistorik",
            "uuid": "04c78fc2-72d2-4d02-b55f-807af19eac48",
            "validity": {
                "from": "2016-01-01",
                "to": "2018-12-31",
            },
        },
        {
            "user_key": "root",
            "name": "Overordnet Enhed",
            "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
            "validity": {
                "from": "2016-01-01",
                "to": None,
            },
        },
        {
            "user_key": "social_og_sundhed-løn",
            "name": "Social og sundhed",
            "uuid": "5942ce50-2be8-476f-914b-6769a888a7c8",
            "validity": {
                "from": "2017-01-01",
                "to": None,
            },
        },
        {
            "user_key": "social-sundhed",
            "name": "Social og sundhed",
            "uuid": "68c5d78e-ae26-441f-a143-0103eca8b62a",
            "validity": {
                "from": "2017-01-01",
                "to": None,
            },
        },
        {
            "user_key": "fil",
            "name": "Filosofisk Institut",
            "uuid": "85715fc7-925d-401b-822d-467eb4b163b6",
            "validity": {
                "from": "2016-01-01",
                "to": None,
            },
        },
        {
            "user_key": "hum",
            "name": "Humanistisk fakultet",
            "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            "validity": {
                "from": "2016-01-01",
                "to": None,
            },
        },
        {
            "user_key": "løn",
            "name": "Lønorganisation",
            "uuid": "b1f69701-86d8-496e-a3f1-ccef18ac1958",
            "validity": {"from": "2017-01-01", "to": None},
        },
        {
            "user_key": "samf",
            "name": "Samfundsvidenskabelige fakultet",
            "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
            "validity": {
                "from": "2017-01-01",
                "to": None,
            },
        },
        {
            "user_key": "hist",
            "name": "Historisk Institut",
            "uuid": "da77153e-30f3-4dc2-a611-ee912a28d8aa",
            "validity": {
                "from": "2016-01-01",
                "to": "2018-12-31",
            },
        },
        {
            "user_key": "skole-børn",
            "name": "Skole og Børn",
            "uuid": "dad7d0ad-c7a9-4a94-969d-464337e31fec",
            "validity": {
                "from": "2017-01-01",
                "to": None,
            },
        },
        {
            "name": "Fake Corp With Addrs",
            "user_key": "fake-orgunit-addrs",
            "uuid": "f494ad89-039d-478e-91f2-a63566554666",
            "validity": {"from": "2016-01-01", "to": None},
        },
        {
            "user_key": "it_sup",
            "name": "IT-Support",
            "uuid": "fa2e23c9-860a-4c90-bcc6-2c0721869a25",
            "validity": {
                "from": "2016-01-01",
                "to": None,
            },
        },
    ]
    response = service_client.request(
        "GET", "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/ou/", params=params
    )
    assert response.status_code == 200
    assert response.json() == expected(result_list)


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "type,uuid,params,has_data",
    [
        # user
        (
            "e",
            "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            {"only_primary_uuid": "1"},
            True,
        ),
        # past
        (
            "e",
            "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            {"validity": "past"},
            False,
        ),
        # future
        (
            "e",
            "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            {"validity": "future"},
            False,
        ),
        (
            "e",
            "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            {"at": "2016-01-01", "validity": "future", "only_primary_uuid": "1"},
            True,
        ),
    ],
)
def test_engagement(
    service_client: TestClient,
    type: str,
    uuid: str,
    params: dict[str, str],
    has_data: bool,
) -> None:
    andersand = [
        {
            "job_function": {
                "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
            },
            "org_unit": {
                "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            },
            "person": {
                "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            },
            "engagement_type": {
                "uuid": "06f95678-166a-455a-a2ab-121a8d92ea23",
            },
            "uuid": "d000591f-8705-4324-897a-075e3623f37b",
            "user_key": "bvn",
            "primary": None,
            "is_primary": None,
            "fraction": None,
            "extension_1": "test1",
            "extension_2": "test2",
            "extension_3": None,
            "extension_4": None,
            "extension_5": None,
            "extension_6": None,
            "extension_7": None,
            "extension_8": None,
            "extension_9": "test9",
            "extension_10": None,
            "validity": {
                "from": "2017-01-01",
                "to": None,
            },
        }
    ]
    response = service_client.request(
        "GET", f"/service/{type}/{uuid}/details/engagement", params=params
    )
    assert response.status_code == 200
    assert response.json() == (andersand if has_data else [])


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "type,uuid,count",
    [
        ("ou", "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e", 3),
        ("e", "6ee24785-ee9a-4502-81c2-7697009c9053", 0),
        ("e", "00000000-0000-0000-0000-000000000000", 0),
    ],
)
def test_engagement_count(
    service_client: TestClient, type: str, uuid: str, count: int
) -> None:
    response = service_client.request(
        "GET", f"/service/{type}/{uuid}/details/engagement"
    )
    assert response.status_code == 200
    assert len(response.json()) == count


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_leave(service_client: TestClient) -> None:
    expected = [
        {
            "engagement": {"uuid": "d000591f-8705-4324-897a-075e3623f37b"},
            "leave_type": {"uuid": "bf65769c-5227-49b4-97c5-642cfbe41aa1"},
            "person": {"uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"},
            "user_key": "bvn",
            "uuid": "b807628c-030c-4f5f-a438-de41c1f26ba5",
            "validity": {"from": "2017-01-01", "to": None},
        }
    ]

    response = service_client.request(
        "GET",
        "/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a/details/leave",
        params={"only_primary_uuid": "1"},
    )
    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "type,uuid,params,has_data",
    [
        # user
        ("e", "53181ed2-f1de-4c4a-a8fd-ab358c2c454a", {"only_primary_uuid": "1"}, True),
        # past
        (
            "e",
            "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            {"validity": "past"},
            False,
        ),
        # future
        (
            "e",
            "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            {"validity": "future"},
            False,
        ),
        (
            "e",
            "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            {"at": "2016-01-01", "validity": "future", "only_primary_uuid": "1"},
            True,
        ),
        # mixed
        (
            "ou",
            "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            {"only_primary_uuid": "1"},
            True,
        ),
        (
            "e",
            "6ee24785-ee9a-4502-81c2-7697009c9053",
            {},
            False,
        ),
        (
            "e",
            "00000000-0000-0000-0000-000000000000",
            {},
            False,
        ),
    ],
)
def test_manager(
    service_client: TestClient,
    type: str,
    uuid: str,
    params: dict[str, str],
    has_data: bool,
) -> None:
    func = [
        {
            "manager_level": {
                "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
            },
            "person": {
                "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            },
            "org_unit": {
                "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            },
            "manager_type": {
                "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
            },
            "responsibility": [{"uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6"}],
            "uuid": "05609702-977f-4869-9fb4-50ad74c6999a",
            "user_key": "be736ee5-5c44-4ed9-b4a4-15ffa19e2848",
            "validity": {
                "from": "2017-01-01",
                "to": None,
            },
        }
    ]
    response = service_client.request(
        "GET", f"/service/{type}/{uuid}/details/manager", params=params
    )
    assert response.status_code == 200
    assert response.json() == (func if has_data else [])


not_found_error = {
    "description": "Not found.",
    "error": True,
    "error_key": "E_NOT_FOUND",
    "status": 404,
}


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "url,status_code,expected",
    [
        ("/service/o/00000000-0000-0000-0000-000000000000/f/", 200, []),
        (
            "/service/o/00000000-0000-0000-0000-000000000000/f/address_type/",
            404,
            not_found_error,
        ),
        (
            "/service/o/00000000-0000-0000-0000-000000000000/f/kaflaflibob/",
            404,
            not_found_error,
        ),
        (
            "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/kaflaflibob/",
            404,
            not_found_error,
        ),
        (
            "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/",
            200,
            [
                {
                    "description": "",
                    "path": "/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/engagement_job_function/",
                    "user_key": "engagement_job_function",
                    "uuid": "1a6045a2-7a8e-4916-ab27-b2402e64f2be",
                },
                {
                    "description": "",
                    "path": "/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/primary_type/",
                    "user_key": "primary_type",
                    "uuid": "1f6f34d8-d065-4bb7-9af0-738d25dc0fbf",
                },
                {
                    "description": "",
                    "path": "/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/kle_number/",
                    "user_key": "kle_number",
                    "uuid": "27935dbb-c173-4116-a4b5-75022315749d",
                },
                {
                    "description": "",
                    "path": "/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/org_unit_address_type/",
                    "user_key": "org_unit_address_type",
                    "uuid": "3c44e5d2-7fef-4448-9bf6-449bf414ec49",
                },
                {
                    "description": "",
                    "path": "/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/engagement_type/",
                    "user_key": "engagement_type",
                    "uuid": "3e702dd1-4103-4116-bb2d-b150aebe807d",
                },
                {
                    "description": "",
                    "path": "/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/org_unit_hierarchy/",
                    "user_key": "org_unit_hierarchy",
                    "uuid": "403eb28f-e21e-bdd6-3612-33771b098a12",
                },
                {
                    "description": "",
                    "path": "/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/responsibility/",
                    "user_key": "responsibility",
                    "uuid": "452e1dd0-658b-477a-8dd8-efba105c06d6",
                },
                {
                    "description": "",
                    "path": "/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/role/",
                    "user_key": "role",
                    "uuid": "68ba77bc-4d57-43e2-9c24-0c9eda5fddc7",
                },
                {
                    "description": "",
                    "path": "/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/org_unit_level/",
                    "user_key": "org_unit_level",
                    "uuid": "77c39616-dd98-4cf5-87fb-cdb9f3a0e455",
                },
                {
                    "description": "",
                    "path": "/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/kle_aspect/",
                    "user_key": "kle_aspect",
                    "uuid": "8a29b2cf-ef98-46f4-9794-0e39354d6ddf",
                },
                {
                    "description": "",
                    "path": "/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/leave_type/",
                    "user_key": "leave_type",
                    "uuid": "99a9d0ab-615e-4e99-8a43-bc9d3cea8438",
                },
                {
                    "description": "",
                    "path": "/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/manager_type/",
                    "user_key": "manager_type",
                    "uuid": "a22f8575-89b4-480b-a7ba-b3f1372e25a4",
                },
                {
                    "description": "",
                    "path": "/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/employee_address_type/",
                    "user_key": "employee_address_type",
                    "uuid": "baddc4eb-406e-4c6b-8229-17e4a21d3550",
                },
                {
                    "description": "",
                    "path": "/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/time_planning/",
                    "user_key": "time_planning",
                    "uuid": "c4ad4c87-28a8-4d5c-afeb-b59de9c9f549",
                },
                {
                    "description": "",
                    "path": "/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/visibility/",
                    "user_key": "visibility",
                    "uuid": "c9f103c7-3d53-47c0-93bf-ccb34d044a3f",
                },
                {
                    "description": "",
                    "path": "/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/manager_level/",
                    "user_key": "manager_level",
                    "uuid": "d56f174d-c45d-4b55-bdc6-c57bf68238b9",
                },
                {
                    "description": "",
                    "path": "/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/association_type/",
                    "user_key": "association_type",
                    "uuid": "ef71fe9c-7901-48e2-86d8-84116e210202",
                },
                {
                    "description": "",
                    "path": "/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/org_unit_type/",
                    "user_key": "org_unit_type",
                    "uuid": "fc917e7c-fc3b-47c2-8aa5-a0383342a280",
                },
            ],
        ),
        (
            "/service/c/32547559-cfc1-4d97-94c6-70b192eff825/",
            200,
            {
                "example": None,
                "name": "Afdeling",
                "owner": None,
                "scope": None,
                "user_key": "afd",
                "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
            },
        ),
        (
            "/service/c/32547559-cfc1-4d97-94c6-70b192eff825/?full_name=1&facet=1&top_level_facet=1",
            200,
            {
                "example": None,
                "facet": org_unit_type_facet,
                "full_name": "Afdeling",
                "name": "Afdeling",
                "owner": None,
                "scope": None,
                "top_level_facet": org_unit_type_facet,
                "user_key": "afd",
                "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
            },
        ),
        (
            "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/org_unit_type/",
            200,
            {
                "data": {
                    "offset": 0,
                    "total": 3,
                    "items": [
                        {
                            "example": None,
                            "name": "Afdeling",
                            "owner": None,
                            "published": "Publiceret",
                            "scope": None,
                            "user_key": "afd",
                            "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                        },
                        {
                            "example": None,
                            "name": "Fakultet",
                            "owner": None,
                            "published": "Publiceret",
                            "scope": None,
                            "user_key": "fak",
                            "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        },
                        {
                            "example": None,
                            "name": "Institut",
                            "owner": None,
                            "published": "Publiceret",
                            "scope": None,
                            "user_key": "inst",
                            "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                        },
                    ],
                },
                "description": "",
                "path": "/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/org_unit_type/",
                "user_key": "org_unit_type",
                "uuid": "fc917e7c-fc3b-47c2-8aa5-a0383342a280",
            },
        ),
        (
            "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/org_unit_type/?full_name=1&facet=1&top_level_facet=1",
            200,
            {
                "data": {
                    "offset": 0,
                    "total": 3,
                    "items": [
                        {
                            "example": None,
                            "facet": org_unit_type_facet,
                            "full_name": "Afdeling",
                            "name": "Afdeling",
                            "owner": None,
                            "published": "Publiceret",
                            "scope": None,
                            "top_level_facet": org_unit_type_facet,
                            "user_key": "afd",
                            "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                        },
                        {
                            "example": None,
                            "facet": org_unit_type_facet,
                            "full_name": "Fakultet",
                            "name": "Fakultet",
                            "owner": None,
                            "published": "Publiceret",
                            "scope": None,
                            "top_level_facet": org_unit_type_facet,
                            "user_key": "fak",
                            "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        },
                        {
                            "example": None,
                            "facet": org_unit_type_facet,
                            "full_name": "Institut",
                            "name": "Institut",
                            "owner": None,
                            "published": "Publiceret",
                            "scope": None,
                            "top_level_facet": org_unit_type_facet,
                            "user_key": "inst",
                            "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                        },
                    ],
                },
                "description": "",
                "path": "/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/org_unit_type/",
                "user_key": "org_unit_type",
                "uuid": "fc917e7c-fc3b-47c2-8aa5-a0383342a280",
            },
        ),
        (
            "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/org_unit_address_type/",
            200,
            {
                "data": {
                    "offset": 0,
                    "total": 6,
                    "items": [
                        {
                            "example": "20304060",
                            "name": "Telefon",
                            "owner": None,
                            "published": "Publiceret",
                            "scope": "PHONE",
                            "user_key": "OrgEnhedTelefon",
                            "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                        },
                        {
                            "example": "<UUID>",
                            "name": "Postadresse",
                            "owner": None,
                            "published": "Publiceret",
                            "scope": "DAR",
                            "user_key": "OrgEnhedPostadresse",
                            "uuid": "28d71012-2919-4b67-a2f0-7b59ed52561e",
                        },
                        {
                            "example": "test@example.com",
                            "name": "Email",
                            "owner": None,
                            "published": "Publiceret",
                            "scope": "EMAIL",
                            "user_key": "OrgEnhedEmail",
                            "uuid": "73360db1-bad3-4167-ac73-8d827c0c8751",
                        },
                        {
                            "example": "5712345000014",
                            "name": "EAN",
                            "owner": None,
                            "published": "Publiceret",
                            "scope": "EAN",
                            "user_key": "EAN",
                            "uuid": "e34d4426-9845-4c72-b31e-709be85d6fa2",
                        },
                        {
                            "example": "EnAndenAfdeling",
                            "name": "Afdelingskode",
                            "owner": None,
                            "published": "Publiceret",
                            "scope": "TEXT",
                            "user_key": "Afdelingskode",
                            "uuid": "e8ea1a09-d3d4-4203-bfe9-d9a213371337",
                        },
                        {
                            "example": "Åbningstider:\n"
                            "Man-tors: 09:00-15:30\n"
                            "Fre: 09:00-13:00",
                            "name": "Træffetid",
                            "owner": None,
                            "published": "Publiceret",
                            "scope": "TEXT",
                            "user_key": "ContactOpenHours",
                            "uuid": "e8ea1a09-d3d4-4203-bfe9-d9a2da100f3b",
                        },
                    ],
                },
                "description": "",
                "path": "/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                "/f/org_unit_address_type/",
                "user_key": "org_unit_address_type",
                "uuid": "3c44e5d2-7fef-4448-9bf6-449bf414ec49",
            },
        ),
    ],
)
def test_facet(service_client: TestClient, url, status_code, expected) -> None:
    response = service_client.request("GET", url)
    assert response.status_code == status_code
    assert response.json() == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "type,uuid,expected",
    [
        # fedtmule
        (
            "e",
            "6ee24785-ee9a-4502-81c2-7697009c9053",
            {
                "address": True,
                "association": False,
                "engagement": False,
                "it": False,
                "kle": False,
                "leave": False,
                "manager": False,
                "org_unit": False,
                "owner": False,
                "related_unit": False,
            },
        ),
        # anders
        (
            "e",
            "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            {
                "address": True,
                "association": True,
                "engagement": True,
                "it": True,
                "kle": False,
                "leave": True,
                "manager": True,
                "org_unit": False,
                "owner": False,
                "related_unit": False,
            },
        ),
        # hum
        (
            "ou",
            "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            {
                "address": True,
                "association": True,
                "engagement": True,
                "it": False,
                "kle": False,
                "leave": False,
                "manager": True,
                "org_unit": True,
                "owner": True,
                "related_unit": True,
            },
        ),
        # samf
        (
            "ou",
            "b688513d-11f7-4efc-b679-ab082a2055d0",
            {
                "address": False,
                "association": False,
                "engagement": False,
                "it": False,
                "kle": False,
                "leave": False,
                "manager": False,
                "org_unit": True,
                "owner": False,
                "related_unit": False,
            },
        ),
        # fil
        (
            "ou",
            "85715fc7-925d-401b-822d-467eb4b163b6",
            {
                "address": False,
                "association": False,
                "engagement": False,
                "it": False,
                "kle": False,
                "leave": False,
                "manager": False,
                "org_unit": True,
                "owner": False,
                "related_unit": False,
            },
        ),
        # hist
        (
            "ou",
            "da77153e-30f3-4dc2-a611-ee912a28d8aa",
            {
                "address": False,
                "association": False,
                "engagement": False,
                "it": False,
                "kle": False,
                "leave": False,
                "manager": False,
                "org_unit": True,
                "owner": False,
                "related_unit": True,
            },
        ),
        # frem
        (
            "ou",
            "04c78fc2-72d2-4d02-b55f-807af19eac48",
            {
                "address": False,
                "association": False,
                "engagement": False,
                "it": True,
                "kle": False,
                "leave": False,
                "manager": False,
                "org_unit": True,
                "owner": False,
                "related_unit": False,
            },
        ),
    ],
)
def test_detail_list(
    service_client: TestClient, type: str, uuid: str, expected: dict[str, bool]
) -> None:
    response = service_client.request("GET", f"/service/{type}/{uuid}/details/")
    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_facet_children(service_client: TestClient) -> None:
    expected = [
        {
            "child_count": 0,
            "name": "Skolepsykolog",
            "user_key": "Skolepsykolog",
            "uuid": "07cea156-1aaf-4c89-bf1b-8e721f704e22",
        },
        {
            "child_count": 0,
            "name": "Specialist",
            "user_key": "specialist",
            "uuid": "890d4ff0-b453-4900-b79b-dbb461eda3ee",
        },
        {
            "child_count": 0,
            "name": "Bogopsætter",
            "user_key": "Bogopsætter",
            "uuid": "f42dd694-f1fd-42a6-8a97-38777b73adc4",
        },
    ]

    response = service_client.request(
        "GET", "/service/f/1a6045a2-7a8e-4916-ab27-b2402e64f2be/children"
    )
    assert response.status_code == 200
    assert response.json() == expected
