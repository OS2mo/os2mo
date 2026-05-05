# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import freezegun
import pytest
from fastapi.testclient import TestClient
from mora import util as mora_util

HUM = {
    "org_unit": [
        {
            "name": "Humanistisk fakultet",
            "user_key": "hum",
            "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            "validity": {
                "from": "2016-01-01",
                "to": None,
            },
        },
        {
            "name": "Overordnet Enhed",
            "user_key": "root",
            "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
            "validity": {
                "from": "2016-01-01",
                "to": None,
            },
        },
    ],
    "uuid": "5c68402c-2a8d-4776-9237-16349fc72648",
    "user_key": "rod <-> hum",
    "validity": {
        "from": "2016-06-01",
        "to": None,
    },
}

HIST = {
    "org_unit": [
        {
            "name": "Historisk Institut",
            "user_key": "hist",
            "uuid": "da77153e-30f3-4dc2-a611-ee912a28d8aa",
            "validity": {
                "from": "2016-01-01",
                "to": "2018-12-31",
            },
        },
        {
            "name": "Overordnet Enhed",
            "user_key": "root",
            "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
            "validity": {
                "from": "2016-01-01",
                "to": None,
            },
        },
    ],
    "uuid": "daa77a4d-6500-483d-b099-2c2eb7fa7a76",
    "user_key": "rod <-> fil",
    "validity": {
        "from": "2017-01-01",
        "to": "2018-12-31",
    },
}


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2017-06-01", tz_offset=2)
@pytest.mark.parametrize(
    "url,expected,message",
    [
        (
            "/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/details/related_unit",
            [HUM, HIST],
            "Overodnet Enhed",
        ),
        (
            "/service/ou/da77153e-30f3-4dc2-a611-ee912a28d8aa/details/related_unit",
            [HIST],
            "Filosofisk Fakultet",
        ),
        (
            "/service/ou/9d07123e-47ac-4a9a-88c8-da82e3a4bc9e/details/related_unit",
            [HUM],
            "Humaninistisk Fakultet",
        ),
        (
            "/service/ou/b688513d-11f7-4efc-b679-ab082a2055d0/details/related_unit",
            [],
            None,
        ),
        # should this be a 404?
        (
            "/service/ou/00000000-0000-0000-0000-000000000000/details/related_unit",
            [],
            None,
        ),
    ],
)
def test_reading(
    service_client: TestClient, url: str, expected: list, message: str | None
) -> None:
    response = service_client.request("GET", url)
    assert response.status_code == 200
    assert response.json() == expected, message


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "url,json,status_code,overrides,freeze_time",
    [
        # past
        (
            "/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/map",
            {
                "destination": [
                    "da77153e-30f3-4dc2-a611-ee912a28d8aa",
                ],
                "validity": {
                    "from": "2017-03-01",
                },
            },
            400,
            {},
            None,
        ),
        # outside
        (
            "/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/map",
            {
                "destination": [
                    "da77153e-30f3-4dc2-a611-ee912a28d8aa",
                ],
                "validity": {
                    "from": "2019-01-01",
                },
            },
            400,
            {},
            None,
        ),
        # accross a change
        (
            "/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/map",
            {
                "destination": [
                    "04c78fc2-72d2-4d02-b55f-807af19eac48",
                ],
                "validity": {
                    "from": "2017-06-01",
                },
            },
            400,
            {},
            "2015-03-01",
        ),
        # invalid origin
        (
            "/service/ou/00000000-0000-0000-0000-000000000000/map",
            {
                "destination": [
                    "2874e1dc-85e6-4269-823a-e1125484dfd3",
                ],
                "validity": {
                    "from": "2017-06-01",
                },
            },
            404,
            {
                "description": "Org unit not found.",
                "error_key": "E_ORG_UNIT_NOT_FOUND",
                "org_unit_uuid": ["00000000-0000-0000-0000-000000000000"],
            },
            None,
        ),
        # invalid destination
        (
            "/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/map",
            {
                "destination": [
                    "00000000-0000-0000-0000-000000000000",
                ],
                "validity": {
                    "from": "2017-06-01",
                },
            },
            404,
            {
                "description": "Org unit not found.",
                "error_key": "E_ORG_UNIT_NOT_FOUND",
                "org_unit_uuid": ["00000000-0000-0000-0000-000000000000"],
            },
            None,
        ),
    ],
)
def test_validation(
    service_client: TestClient,
    url: str,
    json: dict,
    status_code: int,
    overrides: dict,
    freeze_time: str | None,
) -> None:
    expected = {
        "description": "Date range exceeds validity range of associated org unit.",
        "error": True,
        "error_key": "V_DATE_OUTSIDE_ORG_UNIT_RANGE",
        "org_unit_uuid": [json["destination"][0]],
        "status": status_code,
    }
    expected.update(overrides)
    with freezegun.freeze_time(freeze_time or "2017-06-01"):
        response = service_client.request("POST", url, json=json)
        assert response.status_code == status_code
        assert response.json() == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_writing(service_client: TestClient) -> None:
    response = service_client.request(
        "POST",
        "/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/map",
        json={
            "destination": [
                "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                "b688513d-11f7-4efc-b679-ab082a2055d0",
            ],
            "validity": {
                "from": "2017-06-01",
            },
        },
    )
    assert response.status_code == 200
    r = response.json()

    assert r.keys() == {"added", "deleted", "unchanged"}
    assert r["deleted"] == ["daa77a4d-6500-483d-b099-2c2eb7fa7a76"]
    assert r["unchanged"] == ["9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"]
    (functionid,) = r["added"]

    samf = {
        "org_unit": [
            {
                "name": "Overordnet Enhed",
                "user_key": "root",
                "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                "validity": {
                    "from": "2016-01-01",
                    "to": None,
                },
            },
            {
                "name": "Samfundsvidenskabelige fakultet",
                "user_key": "samf",
                "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
                "validity": {
                    "from": "2017-01-01",
                    "to": None,
                },
            },
        ],
        "uuid": functionid,
        "user_key": "root <-> samf",
        "validity": {
            "from": "2017-06-01",
            "to": None,
        },
    }

    response = service_client.request(
        "GET", "/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/details/related_unit"
    )
    assert response.status_code == 200
    r = response.json()
    assert samf in r
    assert HUM in r

    response = service_client.request(
        "GET", "/service/ou/9d07123e-47ac-4a9a-88c8-da82e3a4bc9e/details/related_unit"
    )
    assert response.status_code == 200
    assert response.json() == [HUM], "Humaninistisk Fakultet"

    response = service_client.request(
        "GET", "/service/ou/b688513d-11f7-4efc-b679-ab082a2055d0/details/related_unit"
    )
    assert response.status_code == 200
    assert response.json() == [samf]

    response = service_client.request(
        "GET", "/service/ou/da77153e-30f3-4dc2-a611-ee912a28d8aa/details/related_unit"
    )
    assert response.status_code == 200
    assert response.json() == [], "Historisk Institut"

    response = service_client.request(
        "GET", "/service/ou/da77153e-30f3-4dc2-a611-ee912a28d8aa/details/related_unit"
    )
    assert response.status_code == 200
    assert response.json() == []

    # past
    hist = mora_util.set_obj_value(HIST, ("validity", "to"), "2017-05-31")

    response = service_client.request(
        "GET",
        "/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3"
        "/details/related_unit?validity=past",
    )
    assert response.status_code == 200
    assert response.json() == [hist], "Overordnet Enhed, past"

    response = service_client.request(
        "GET",
        "/service/ou/da77153e-30f3-4dc2-a611-ee912a28d8aa"
        "/details/related_unit?validity=past",
    )
    assert response.status_code == 200
    assert response.json() == [hist], "Historisk Institut, past"

    response = service_client.request(
        "GET",
        "/service/ou/9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
        "/details/related_unit?validity=past",
    )
    assert response.status_code == 200
    assert response.json() == [], "Humaninistisk Fakultet, past"

    response = service_client.request(
        "GET",
        "/service/ou/b688513d-11f7-4efc-b679-ab082a2055d0"
        "/details/related_unit?validity=past",
    )
    assert response.status_code == 200
    assert response.json() == []
