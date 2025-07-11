# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import AsyncMock
from unittest.mock import call

import freezegun
from fastapi.testclient import TestClient
from oio_rest.organisation import Organisation


@freezegun.freeze_time("2016-06-06")
def test_autocomplete_no_municipality(monkeypatch, service_client: TestClient) -> None:
    arrange = AsyncMock(
        return_value={
            "results": [
                [
                    {
                        "id": "00000000-0000-0000-0000-000000000000",
                        "registreringer": [
                            {
                                "attributter": {
                                    "organisationegenskaber": [
                                        {
                                            "brugervendtnoegle": "bvn",
                                            "organisationsnavn": "onvn",
                                        }
                                    ]
                                },
                                "tilstande": {
                                    "organisationgyldighed": [
                                        {
                                            "gyldighed": "Aktiv",
                                        }
                                    ]
                                },
                            }
                        ],
                    }
                ]
            ]
        },
    )

    monkeypatch.setattr(Organisation, "get_objects_direct", arrange)

    mo_url = (
        "/service/o/00000000-0000-0000-0000-000000000000/address_autocomplete/?q=42"
    )

    response = service_client.request("GET", mo_url)
    assert response.status_code == 400
    assert response.json() == {
        "error": True,
        "error_key": "E_NO_LOCAL_MUNICIPALITY",
        "description": "No local municipality found.",
        "status": 400,
    }
    assert arrange.await_count == 2

    arrange.assert_has_calls(
        [
            call(
                [
                    ("virkningfra", "-infinity"),
                    ("virkningtil", "infinity"),
                    ("konsolider", "True"),
                    ("bvn", "%"),
                    ("list", "True"),
                ]
            ),
            call(
                [
                    ("virkningfra", "2016-06-06T02:00:00+02:00"),
                    ("virkningtil", "2016-06-06T02:00:00.001000+02:00"),
                    ("konsolider", "True"),
                    ("uuid", "00000000-0000-0000-0000-000000000000"),
                ]
            ),
        ]
    )


@freezegun.freeze_time("2016-06-06")
def test_autocomplete_invalid_municipality(
    monkeypatch, service_client: TestClient
) -> None:
    arrange = AsyncMock(
        return_value={
            "results": [
                [
                    {
                        "id": "00000000-0000-0000-0000-000000000000",
                        "registreringer": [
                            {
                                "attributter": {
                                    "organisationegenskaber": [
                                        {
                                            "brugervendtnoegle": "bvn",
                                            "organisationsnavn": "onavn",
                                        }
                                    ]
                                },
                                "relationer": {
                                    "myndighed": [
                                        {
                                            "urn": "kaflaflibob",
                                        }
                                    ]
                                },
                                "tilstande": {
                                    "organisationgyldighed": [
                                        {
                                            "gyldighed": "Aktiv",
                                        }
                                    ]
                                },
                            }
                        ],
                    }
                ]
            ]
        },
    )

    monkeypatch.setattr(Organisation, "get_objects_direct", arrange)

    mo_url = (
        "/service/o/00000000-0000-0000-0000-000000000000/address_autocomplete/?q=42"
    )

    response = service_client.request("GET", mo_url)
    assert response.status_code == 400
    assert response.json() == {
        "error": True,
        "error_key": "E_NO_LOCAL_MUNICIPALITY",
        "description": "No local municipality found.",
        "status": 400,
    }
    assert arrange.await_count == 2

    arrange.assert_has_calls(
        [
            call(
                [
                    ("virkningfra", "-infinity"),
                    ("virkningtil", "infinity"),
                    ("konsolider", "True"),
                    ("bvn", "%"),
                    ("list", "True"),
                ]
            ),
            call(
                [
                    ("virkningfra", "2016-06-06T02:00:00+02:00"),
                    ("virkningtil", "2016-06-06T02:00:00.001000+02:00"),
                    ("konsolider", "True"),
                    ("uuid", "00000000-0000-0000-0000-000000000000"),
                ]
            ),
        ]
    )


@freezegun.freeze_time("2016-06-06")
def test_autocomplete_missing_org(monkeypatch, service_client: TestClient) -> None:
    arrange = AsyncMock(return_value={"results": []})

    mo_url = (
        "/service/o/00000000-0000-0000-0000-000000000000/address_autocomplete/?q=42"
    )

    monkeypatch.setattr(Organisation, "get_objects_direct", arrange)

    response = service_client.request("GET", mo_url)
    assert response.status_code == 400
    assert response.json() == {
        "error": True,
        "error_key": "E_NO_LOCAL_MUNICIPALITY",
        "description": "No local municipality found.",
        "status": 400,
    }

    arrange.assert_called_once_with(
        [
            ("virkningfra", "-infinity"),
            ("virkningtil", "infinity"),
            ("konsolider", "True"),
            ("bvn", "%"),
            ("list", "True"),
        ]
    )


@freezegun.freeze_time("2017-07-28")
def test_autocomplete_global(respx_mock, service_client: TestClient) -> None:
    found = [
        {
            "location": {
                "name": "Strandlodsvej 25M, 2300 K\u00f8benhavn S",
                "uuid": "18fbd56e-c6b2-4d0f-bb08-80133edb896e",
            }
        },
        {
            "location": {
                "name": "Strandlodsvej 25M, 1. th, 2300 K\u00f8benhavn S",
                "uuid": "b18f681b-dcce-4a1f-9231-08182653dbd9",
            }
        },
        {
            "location": {
                "name": "Strandlodsvej 25M, 1. tv, 2300 K\u00f8benhavn S",
                "uuid": "21483493-bf6d-4cdd-badd-74bc5109c7b1",
            }
        },
        {
            "location": {
                "name": "Strandlodsvej 25M, 2. th, 2300 K\u00f8benhavn S",
                "uuid": "22bf4e3e-14f3-4096-b479-2e8d4ac090fb",
            }
        },
        {
            "location": {
                "name": "Strandlodsvej 25M, 2. tv, 2300 K\u00f8benhavn S",
                "uuid": "d4764afd-f5f1-4038-9298-9148bcb56421",
            }
        },
        {
            "location": {
                "name": "Strandlodsvej 25M, 3. th, 2300 K\u00f8benhavn S",
                "uuid": "13deac37-805b-4024-a6dc-4b5f6808571c",
            }
        },
        {
            "location": {
                "name": "Strandlodsvej 25M, 3. tv, 2300 K\u00f8benhavn S",
                "uuid": "2bd96c7d-e9b5-449b-889c-f09a4c1fae50",
            }
        },
        {
            "location": {
                "name": "Strandlodsvej 25M, 4. th, 2300 K\u00f8benhavn S",
                "uuid": "c5871526-6f4f-425c-bd3f-05b837df24cb",
            }
        },
        {
            "location": {
                "name": "Strandlodsvej 25M, 4. tv, 2300 K\u00f8benhavn S",
                "uuid": "6ee8b42e-bfc2-42d3-974f-47791c99b375",
            }
        },
        {
            "location": {
                "name": "Strandlodsvej 25M, 5. th, 2300 K\u00f8benhavn S",
                "uuid": "fd3fceb2-860a-4c15-b57f-795cbfda5882",
            }
        },
        {
            "location": {
                "name": "Strandlodsvej 25M, 5. tv, 2300 K\u00f8benhavn S",
                "uuid": "8aa7e68d-e451-43c7-9c02-705ea7a9bb40",
            }
        },
    ]
    mo_url1 = (
        "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/"
        "address_autocomplete/?q=Strandlodsvej+25M&global=1"
    )
    mo_url2 = (
        "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/"
        "address_autocomplete/?q=Strandlodsvej+25M&global=true"
    )

    respx_mock.get(
        "https://api.dataforsyningen.dk/adresser/autocomplete",
        params={"noformat": 1, "q": "Strandlodsvej 25M", "per_side": 10},
    ).pass_through()
    respx_mock.get(
        "https://api.dataforsyningen.dk/adgangsadresser/autocomplete",
        params={"noformat": 1, "q": "Strandlodsvej 25M", "per_side": 5},
    ).pass_through()

    response = service_client.request("GET", mo_url1)
    assert response.status_code == 200
    assert response.json() == found

    response = service_client.request("GET", mo_url2)
    assert response.status_code == 200
    assert response.json() == found
