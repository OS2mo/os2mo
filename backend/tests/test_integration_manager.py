# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from unittest.mock import patch
from uuid import UUID

import freezegun
import pytest
from fastapi.testclient import TestClient
from mora import lora
from mora import util as mora_util
from more_itertools import one

from tests.cases import assert_registrations_equal
from tests.conftest import GraphAPIPost

mock_uuid = "1eb680cd-d8ec-4fd2-8ca0-dce2d03f59a5"
userid = "6ee24785-ee9a-4502-81c2-7697009c9053"
userid2 = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
manager_uuid = "05609702-977f-4869-9fb4-50ad74c6999a"


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "operation,userid,payload,expected",
    [
        # Base case
        (
            "create",
            userid,
            {
                "type": "manager",
                "org_unit": {"uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "person": {"uuid": userid},
                "responsibility": [
                    {"uuid": "ca76a441-6226-404f-88a9-31e02e420e52"},
                    {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                ],
                "manager_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
                "manager_level": {"uuid": "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0"},
                "user_key": "1234",
                "validity": {
                    "from": "2017-12-01",
                    "to": "2017-12-01",
                },
            },
            {
                "livscykluskode": "Importeret",
                "tilstande": {
                    "organisationfunktiongyldighed": [
                        {
                            "virkning": {
                                "to_included": False,
                                "to": "2017-12-02 00:00:00+01",
                                "from_included": True,
                                "from": "2017-12-01 00:00:00+01",
                            },
                            "gyldighed": "Aktiv",
                        }
                    ]
                },
                "note": "Oprettet i MO",
                "relationer": {
                    "tilknyttedeorganisationer": [
                        {
                            "virkning": {
                                "to_included": False,
                                "to": "2017-12-02 00:00:00+01",
                                "from_included": True,
                                "from": "2017-12-01 00:00:00+01",
                            },
                            "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        }
                    ],
                    "tilknyttedebrugere": [
                        {
                            "virkning": {
                                "to_included": False,
                                "to": "2017-12-02 00:00:00+01",
                                "from_included": True,
                                "from": "2017-12-01 00:00:00+01",
                            },
                            "uuid": "6ee24785-ee9a-4502-81c2-7697009c9053",
                        }
                    ],
                    "opgaver": [
                        {
                            "objekttype": "lederansvar",
                            "virkning": {
                                "to_included": False,
                                "to": "2017-12-02 00:00:00+01",
                                "from_included": True,
                                "from": "2017-12-01 00:00:00+01",
                            },
                            "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                        },
                        {
                            "objekttype": "lederansvar",
                            "virkning": {
                                "to_included": False,
                                "to": "2017-12-02 00:00:00+01",
                                "from_included": True,
                                "from": "2017-12-01 00:00:00+01",
                            },
                            "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
                        },
                        {
                            "objekttype": "lederniveau",
                            "virkning": {
                                "to_included": False,
                                "to": "2017-12-02 00:00:00+01",
                                "from_included": True,
                                "from": "2017-12-01 00:00:00+01",
                            },
                            "uuid": "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0",
                        },
                    ],
                    "organisatoriskfunktionstype": [
                        {
                            "virkning": {
                                "to_included": False,
                                "to": "2017-12-02 00:00:00+01",
                                "from_included": True,
                                "from": "2017-12-01 00:00:00+01",
                            },
                            "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
                        }
                    ],
                    "tilknyttedeenheder": [
                        {
                            "virkning": {
                                "to_included": False,
                                "to": "2017-12-02 00:00:00+01",
                                "from_included": True,
                                "from": "2017-12-01 00:00:00+01",
                            },
                            "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        }
                    ],
                },
                "attributter": {
                    "organisationfunktionegenskaber": [
                        {
                            "virkning": {
                                "to_included": False,
                                "to": "2017-12-02 00:00:00+01",
                                "from_included": True,
                                "from": "2017-12-01 00:00:00+01",
                            },
                            "brugervendtnoegle": "1234",
                            "funktionsnavn": "Leder",
                        }
                    ]
                },
            },
        ),
        # No overwrite
        (
            "edit",
            userid2,
            {
                "type": "manager",
                "uuid": manager_uuid,
                "data": {
                    "org_unit": {"uuid": "85715fc7-925d-401b-822d-467eb4b163b6"},
                    "person": {
                        "uuid": userid2,
                    },
                    "responsibility": [
                        {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"}
                    ],
                    "manager_level": {"uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec"},
                    "manager_type": {"uuid": "e34d4426-9845-4c72-b31e-709be85d6fa2"},
                    "user_key": "kaflaflibob",
                    "validity": {
                        "from": "2018-04-01",
                    },
                },
            },
            {
                "note": "Rediger leder",
                "relationer": {
                    "opgaver": [
                        {
                            "objekttype": "lederniveau",
                            "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2018-04-01 00:00:00+02",
                                "to": "infinity",
                            },
                        },
                        {
                            "objekttype": "lederniveau",
                            "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2017-01-01 00:00:00+01",
                                "to": "2018-04-01 00:00:00+02",
                            },
                        },
                        {
                            "objekttype": "lederansvar",
                            "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2017-01-01 00:00:00+01",
                                "to": "2018-04-01 00:00:00+02",
                            },
                        },
                        {
                            "objekttype": "lederansvar",
                            "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2018-04-01 00:00:00+02",
                                "to": "infinity",
                            },
                        },
                    ],
                    "organisatoriskfunktionstype": [
                        {
                            "uuid": "e34d4426-9845-4c72-b31e-709be85d6fa2",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2018-04-01 00:00:00+02",
                                "to": "infinity",
                            },
                        },
                        {
                            "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
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
                            "uuid": "414044e0-fe5f-4f82-be20-1e107ad50e80",
                            "virkning": {
                                "from": "2017-01-01 00:00:00+01",
                                "from_included": True,
                                "to": "infinity",
                                "to_included": False,
                            },
                        }
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
                    "tilknyttedeenheder": [
                        {
                            "uuid": "85715fc7-925d-401b-822d-467eb4b163b6",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2018-04-01 00:00:00+02",
                                "to": "infinity",
                            },
                        },
                        {
                            "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2017-01-01 00:00:00+01",
                                "to": "2018-04-01 00:00:00+02",
                            },
                        },
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
                        },
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
                            "brugervendtnoegle": "be736ee5-5c44-4ed9-b4a4-15ffa19e2848",
                            "funktionsnavn": "Leder",
                        },
                        {
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2018-04-01 00:00:00+02",
                                "to": "infinity",
                            },
                            "brugervendtnoegle": "kaflaflibob",
                            "funktionsnavn": "Leder",
                        },
                    ]
                },
            },
        ),
        # Overwrite
        (
            "edit",
            userid2,
            {
                "type": "manager",
                "uuid": manager_uuid,
                "original": {
                    "org_unit": {"uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                    "person": {
                        "uuid": userid2,
                    },
                    "responsibility": [
                        {"uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6"}
                    ],
                    "manager_level": {"uuid": "ca76a441-6226-404f-88a9-31e02e420e52"},
                    "manager_type": {"uuid": "32547559-cfc1-4d97-94c6-70b192eff825"},
                    "validity": {
                        "from": "2017-01-01",
                        "to": None,
                    },
                },
                "data": {
                    "org_unit": {"uuid": "85715fc7-925d-401b-822d-467eb4b163b6"},
                    "responsibility": [
                        {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"}
                    ],
                    "manager_level": {"uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec"},
                    "manager_type": {"uuid": "e34d4426-9845-4c72-b31e-709be85d6fa2"},
                    "validity": {
                        "from": "2018-04-01",
                    },
                },
            },
            {
                "note": "Rediger leder",
                "relationer": {
                    "opgaver": [
                        {
                            "objekttype": "lederansvar",
                            "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2018-04-01 00:00:00+02",
                                "to": "infinity",
                            },
                        },
                        {
                            "objekttype": "lederansvar",
                            "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2017-01-01 00:00:00+01",
                                "to": "2018-04-01 00:00:00+02",
                            },
                        },
                        {
                            "objekttype": "lederniveau",
                            "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2018-04-01 00:00:00+02",
                                "to": "infinity",
                            },
                        },
                        {
                            "objekttype": "lederniveau",
                            "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2017-01-01 00:00:00+01",
                                "to": "2018-04-01 00:00:00+02",
                            },
                        },
                    ],
                    "organisatoriskfunktionstype": [
                        {
                            "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2017-01-01 00:00:00+01",
                                "to": "2018-04-01 00:00:00+02",
                            },
                        },
                        {
                            "uuid": "e34d4426-9845-4c72-b31e-709be85d6fa2",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2018-04-01 00:00:00+02",
                                "to": "infinity",
                            },
                        },
                    ],
                    "tilknyttedefunktioner": [
                        {
                            "uuid": "414044e0-fe5f-4f82-be20-1e107ad50e80",
                            "virkning": {
                                "from": "2017-01-01 00:00:00+01",
                                "from_included": True,
                                "to": "infinity",
                                "to_included": False,
                            },
                        }
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
                    "tilknyttedeenheder": [
                        {
                            "uuid": "85715fc7-925d-401b-822d-467eb4b163b6",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2018-04-01 00:00:00+02",
                                "to": "infinity",
                            },
                        },
                        {
                            "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2017-01-01 00:00:00+01",
                                "to": "2018-04-01 00:00:00+02",
                            },
                        },
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
                                "from": "2018-04-01 00:00:00+02",
                                "to": "infinity",
                            },
                        },
                        {
                            "gyldighed": "Inaktiv",
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2017-01-01 00:00:00+01",
                                "to": "2018-04-01 00:00:00+02",
                            },
                        },
                    ]
                },
                "attributter": {
                    "organisationfunktionegenskaber": [
                        {
                            "virkning": {
                                "from_included": True,
                                "to_included": False,
                                "from": "2017-01-01 00:00:00+01",
                                "to": "infinity",
                            },
                            "brugervendtnoegle": "be736ee5-5c44-4ed9-b4a4-15ffa19e2848",
                            "funktionsnavn": "Leder",
                        }
                    ]
                },
            },
        ),
    ],
)
@freezegun.freeze_time("2017-01-01", tz_offset=1)
@patch("uuid.uuid4", new=lambda: UUID("1eb680cd-d8ec-4fd2-8ca0-dce2d03f59a5"))
async def test_create_manager(
    service_client: TestClient,
    operation: str,
    userid: str,
    payload: dict[str, Any],
    expected: dict[str, Any],
) -> None:
    # Check the POST request
    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

    with patch("uuid.uuid4", new=lambda: UUID(mock_uuid)):
        response = service_client.request(
            "POST", f"/service/details/{operation}", json=payload
        )
        assert response.status_code == 201 if operation == "create" else 200
        managerid = response.json()

    actual = await c.organisationfunktion.get(managerid)
    assert actual is not None
    assert_registrations_equal(expected, actual)


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@patch("uuid.uuid4", new=lambda: UUID(mock_uuid))
@freezegun.freeze_time("2017-01-01", tz_offset=1)
async def test_read_manager_multiple_responsibilities(
    another_transaction,
    service_client: TestClient,
) -> None:
    """Test reading a manager with multiple responsibilities, all valid"""
    manager_uuid = "05609702-977f-4869-9fb4-50ad74c6999a"
    userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

    # inject multiple responsibilities
    c = lora.Connector()

    overwritten_responsibilities = [
        {
            "objekttype": "lederansvar",
            "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
            "virkning": {
                "from": "2017-01-01 00:00:00+01",
                "from_included": True,
                "to": "infinity",
                "to_included": False,
            },
        },
        {
            "objekttype": "lederansvar",
            "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
            "virkning": {
                "from": "2017-01-01 00:00:00+01",
                "from_included": True,
                "to": "infinity",
                "to_included": False,
            },
        },
        {
            "objekttype": "lederniveau",
            "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
            "virkning": {
                "from": "2017-01-01 00:00:00+01",
                "from_included": True,
                "to": "infinity",
                "to_included": False,
            },
        },
    ]

    async with another_transaction():
        await c.organisationfunktion.update(
            {
                "relationer": {
                    "opgaver": overwritten_responsibilities,
                }
            },
            manager_uuid,
        )

    async with another_transaction():
        assert (
            sorted(
                (await c.organisationfunktion.get(manager_uuid))["relationer"][
                    "opgaver"
                ],
                key=mora_util.get_uuid,
            )
            == overwritten_responsibilities
        )

    response = service_client.request(
        "GET", f"/service/e/{userid}/details/manager", params={"only_primary_uuid": 1}
    )
    assert response.status_code == 200
    assert response.json() == [
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
                "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            },
            "responsibility": [
                {
                    "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                },
                {
                    "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
                },
            ],
            "uuid": "05609702-977f-4869-9fb4-50ad74c6999a",
            "user_key": "be736ee5-5c44-4ed9-b4a4-15ffa19e2848",
            "validity": {
                "from": "2017-01-01",
                "to": None,
            },
        }
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@patch("uuid.uuid4", new=lambda: UUID(mock_uuid))
@freezegun.freeze_time("2017-01-01", tz_offset=1)
def test_create_manager_missing_unit(service_client: TestClient) -> None:
    # Check the POST request
    payload = {
        "type": "manager",
        "validity": {
            "from": "2017-12-01",
            "to": "2017-12-01",
        },
    }

    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == 400
    assert response.json() == {
        "description": "Missing org_unit",
        "error": True,
        "error_key": "V_MISSING_REQUIRED_VALUE",
        "key": "org_unit",
        "obj": payload,
        "status": 400,
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@patch("uuid.uuid4", new=lambda: UUID(mock_uuid))
@freezegun.freeze_time("2017-01-01", tz_offset=1)
def test_create_vacant_manager(service_client: TestClient) -> None:
    unit_id = "da77153e-30f3-4dc2-a611-ee912a28d8aa"

    response = service_client.request("GET", f"/service/ou/{unit_id}/details/manager")
    assert response.status_code == 200
    assert response.json() == []

    payload = {
        "type": "manager",
        "org_unit": {
            "uuid": unit_id,
        },
        "responsibility": [
            {
                "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
            }
        ],
        "manager_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
        "manager_level": {"uuid": "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0"},
        "validity": {
            "from": "2016-12-01",
            "to": "2017-12-02",
        },
    }

    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == 201
    function_id = response.json()

    employee_address_type_facet = {
        "description": "",
        "user_key": "employee_address_type",
        "uuid": "baddc4eb-406e-4c6b-8229-17e4a21d3550",
    }
    association_type_facet = {
        "description": "",
        "user_key": "association_type",
        "uuid": "ef71fe9c-7901-48e2-86d8-84116e210202",
    }

    response = service_client.request("GET", f"/service/ou/{unit_id}/details/manager")
    assert response.status_code == 200
    assert response.json() == [
        {
            "manager_level": {
                "example": "test@example.com",
                "facet": employee_address_type_facet,
                "full_name": "Email",
                "name": "Email",
                "owner": None,
                "published": "Publiceret",
                "scope": "EMAIL",
                "top_level_facet": employee_address_type_facet,
                "user_key": "BrugerEmail",
                "uuid": "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0",
            },
            "manager_type": {
                "example": None,
                "facet": association_type_facet,
                "full_name": "Medlem",
                "name": "Medlem",
                "owner": None,
                "published": "Publiceret",
                "scope": None,
                "top_level_facet": association_type_facet,
                "user_key": "medl",
                "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
            },
            "org_unit": {
                "name": "Historisk Institut",
                "user_key": "hist",
                "uuid": "da77153e-30f3-4dc2-a611-ee912a28d8aa",
                "validity": {"from": "2016-01-01", "to": "2018-12-31"},
            },
            "person": None,
            "responsibility": [
                {
                    "example": None,
                    "facet": association_type_facet,
                    "full_name": "Medlem",
                    "name": "Medlem",
                    "owner": None,
                    "published": "Publiceret",
                    "scope": None,
                    "top_level_facet": association_type_facet,
                    "user_key": "medl",
                    "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
                }
            ],
            "uuid": function_id,
            "user_key": mock_uuid,
            "validity": {"from": "2016-12-01", "to": "2017-12-02"},
        }
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@patch("uuid.uuid4", new=lambda: UUID(mock_uuid))
@freezegun.freeze_time("2017-01-01", tz_offset=1)
def test_edit_manager_on_unit(service_client: TestClient) -> None:
    unit_id = "da77153e-30f3-4dc2-a611-ee912a28d8aa"
    user_id = "6ee24785-ee9a-4502-81c2-7697009c9053"

    response = service_client.request(
        "POST",
        "/service/details/create",
        json={
            "type": "manager",
            "org_unit": {
                "uuid": unit_id,
            },
            "responsibility": [
                {
                    "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
                }
            ],
            "manager_type": {"uuid": "62ec821f-4179-4758-bfdf-134529d186e9"},
            "manager_level": {"uuid": "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0"},
            "person": {
                "uuid": user_id,
            },
            "validity": {
                "from": "2016-12-01",
                "to": "2017-12-02",
            },
        },
    )
    assert response.status_code == 201
    function_id = response.json()

    expected = {
        "user_key": mock_uuid,
        "manager_level": {
            "uuid": "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0",
        },
        "manager_type": {
            "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
        },
        "org_unit": {
            "uuid": "da77153e-30f3-4dc2-a611-ee912a28d8aa",
        },
        "person": {
            "uuid": "6ee24785-ee9a-4502-81c2-7697009c9053",
        },
        "responsibility": [
            {
                "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
            }
        ],
        "validity": {"from": "2016-12-01", "to": "2017-12-02"},
    }

    expected["uuid"] = function_id
    response = service_client.request(
        "GET", f"/service/ou/{unit_id}/details/manager", params={"only_primary_uuid": 1}
    )
    assert response.status_code == 200
    assert response.json() == [expected]

    # Change to Vacant
    response = service_client.request(
        "POST",
        "/service/details/edit",
        json={
            "type": "manager",
            "uuid": function_id,
            "data": {
                "person": None,
                "validity": {
                    "from": "2017-12-03",
                    "to": "2017-12-20",
                },
            },
        },
    )
    assert response.status_code == 200
    assert response.json() == function_id

    response = service_client.request(
        "GET", f"/service/ou/{unit_id}/details/manager", params={"only_primary_uuid": 1}
    )
    assert response.status_code == 200
    assert response.json() == [expected]

    # Check future
    future = expected.copy()
    future["person"] = None
    future["validity"] = {
        "from": "2017-12-03",
        "to": "2017-12-20",
    }

    response = service_client.request(
        "GET",
        f"/service/ou/{unit_id}/details/manager",
        params={"only_primary_uuid": 1, "validity": "future"},
    )
    assert response.status_code == 200
    assert response.json() == [future]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
def test_read_no_inherit_manager(service_client: TestClient) -> None:
    # Anders And is manager at humfak
    filins = "85715fc7-925d-401b-822d-467eb4b163b6"
    # We are NOT allowed to inherit Anders And
    response = service_client.request("GET", f"/service/ou/{filins}/details/manager")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
def test_read_inherit_manager_one_level(service_client: TestClient) -> None:
    # Anders And is manager at humfak
    humfak = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
    # There is no manager at filins
    filins = "85715fc7-925d-401b-822d-467eb4b163b6"
    # We must inherit Anders And
    response = service_client.request(
        "GET", f"/service/ou/{filins}/details/manager", params={"inherit_manager": 1}
    )
    assert response.status_code == 200
    inherited_manager = one(response.json())
    assert inherited_manager["org_unit"]["uuid"] == humfak


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
def test_read_inherit_manager_none_found_all_the_way_up(
    service_client: TestClient,
) -> None:
    # There is no manager at samfak
    samfak = "b688513d-11f7-4efc-b679-ab082a2055d0"
    # We must not find no managers
    response = service_client.request(
        "GET", f"/service/ou/{samfak}/details/manager", params={"inherit_manager": 1}
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_create_manager_with_engagement(graphapi_post: GraphAPIPost) -> None:
    # Find two engagements to use
    FIND_ENGAGEMENT = """
    query FindEngagementUUID {
      engagements(limit: "2") {
        objects {
          uuid
        }
      }
    }
    """
    response = graphapi_post(
        FIND_ENGAGEMENT,
    )
    assert response.errors is None
    engagement_1, engagement_2 = response.data["engagements"]["objects"]
    engagement_1_uuid = engagement_1["uuid"]
    engagement_2_uuid = engagement_2["uuid"]

    # Create a manager using the first engagement

    CREATE_MANAGER = """
    mutation CreateManager($input: ManagerCreateInput!) {
      manager_create(input: $input) {
        uuid
        current {
          engagement {
            uuid
          }
        }
      }
    }
    """

    response = graphapi_post(
        CREATE_MANAGER,
        variables={
            "input": {
                "person": "6ee24785-ee9a-4502-81c2-7697009c9053",
                "responsibility": [],
                "org_unit": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                "manager_type": "62ec821f-4179-4758-bfdf-134529d186e9",
                "manager_level": "ca76a441-6226-404f-88a9-31e02e420e52",
                "engagement": engagement_1_uuid,
                "validity": {"from": "2020-01-01"},
            }
        },
    )
    # Assert that the manager was created with the correct engagement
    assert response.errors is None
    assert (
        response.data["manager_create"]["current"]["engagement"]["uuid"]
        == engagement_1_uuid
    )

    # Update the manager with the second engagement
    manager_uuid = response.data["manager_create"]["uuid"]
    UPDATE_MANAGER = """
    mutation UpdateManager($input: ManagerUpdateInput!) {
      manager_update(input: $input) {
        uuid
        current {
          engagement {
            uuid
          }
        }
      }
    }
    """
    response = graphapi_post(
        UPDATE_MANAGER,
        variables={
            "input": {
                "uuid": manager_uuid,
                "engagement": engagement_2_uuid,
                "validity": {"from": "2020-01-01"},
            }
        },
    )
    assert response.errors is None
    assert (
        response.data["manager_update"]["current"]["engagement"]["uuid"]
        == engagement_2_uuid
    )

    # Update the manager to remove the engagement.
    response = graphapi_post(
        UPDATE_MANAGER,
        variables={
            "input": {
                "uuid": manager_uuid,
                "engagement": None,
                "validity": {"from": "2020-01-01"},
            }
        },
    )
    assert response.errors is None
    assert response.data["manager_update"]["current"]["engagement"]["uuid"] is None
