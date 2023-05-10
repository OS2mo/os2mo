# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import uuid
from datetime import datetime
from unittest.mock import MagicMock
from unittest.mock import patch

import freezegun
import pytest
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient

from mora.service.orgunit import config as orgunit_config
from tests.conftest import GQLResponse


# NOTE: Read "backend/tests/graphapi/test_registration.py:11",
# for reasoning behind "@pytest.mark.xfail"


@pytest.fixture
def mock_get_settings():
    with patch.object(
        orgunit_config,
        "get_settings",
        return_value=MagicMock(confdb_autocomplete_v2_use_legacy=False),
    ) as mock_get_settings:
        yield mock_get_settings


@pytest.fixture
def mock_get_settings_custom_attrs():
    with patch.object(
        orgunit_config,
        "get_settings",
        return_value=MagicMock(
            confdb_autocomplete_v2_use_legacy=False,
            confdb_autocomplete_attrs_orgunit=[
                uuid.UUID("e8ea1a09-d3d4-4203-bfe9-d9a213371337"),
            ],
        ),
    ) as mock_get_settings:
        yield mock_get_settings


@pytest.mark.xfail
@pytest.mark.integration_test
@freezegun.freeze_time("2017-01-01", tz_offset=1)
@pytest.mark.usefixtures("load_fixture_data_with_reset")
def test_v2_search_employee_by_uuid(mock_get_settings, service_client: TestClient):
    mock_get_settings.return_value = MagicMock(
        confdb_autocomplete_v2_use_legacy=False,
    )

    at = datetime.now().date()
    query = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
    response = service_client.get(
        f"/service/e/autocomplete/?query={query}&at={at.isoformat()}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                "name": "Anders And",
                "attrs": [
                    {
                        "uuid": "d000591f-8705-4324-897a-075e3623f37b",
                        "title": "Ansat",
                        "value": "bvn",
                    },
                    {
                        "uuid": "fba61e38-b553-47cc-94bf-8c7c3c2a6887",
                        "title": "Email",
                        "value": "bruger@example.com",
                    },
                    {
                        "uuid": "c2153d5d-4a2b-492d-a18c-c498f7bb6221",
                        "title": "Medlem",
                        "value": "bvn",
                    },
                    {
                        "uuid": "aaa8c495-d7d4-4af1-b33a-f4cb27b82c66",
                        "title": "Active Directory",
                        "value": "donald",
                    },
                ],
            }
        ]
    }


@pytest.mark.xfail
@pytest.mark.integration_test
@freezegun.freeze_time("2017-01-01", tz_offset=1)
@pytest.mark.usefixtures("load_fixture_data_with_reset")
def test_v2_search_orgunit_by_uuid(mock_get_settings, service_client: TestClient):
    mock_get_settings.return_value = MagicMock(
        confdb_autocomplete_v2_use_legacy=False,
    )

    at = datetime.now().date()
    query = "f494ad89-039d-478e-91f2-a63566554666"
    response = service_client.get(
        f"/service/ou/autocomplete/?query={query}&at={at.isoformat()}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "uuid": "f494ad89-039d-478e-91f2-a63566554666",
                "name": "Fake Corp With Addrs",
                "path": [],
                "attrs": [],
            }
        ]
    }

    query = "b688513d-11f7-4efc-b679-ab082a2055d0"
    response = service_client.get(
        f"/service/ou/autocomplete/?query={query}&at={at.isoformat()}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
                "name": "Samfundsvidenskabelige fakultet",
                "path": ["Overordnet Enhed", "Samfundsvidenskabelige fakultet"],
                "attrs": [],
            }
        ]
    }


@pytest.mark.xfail
@pytest.mark.integration_test
@freezegun.freeze_time("2017-01-01", tz_offset=1)
@pytest.mark.usefixtures("load_fixture_data_with_reset")
def test_v2_search_orgunit_by_name(mock_get_settings, service_client: TestClient):
    at = datetime.now().date()
    query = "Fake Corp"
    response = service_client.get(
        f"/service/ou/autocomplete/?query={query}&at={at.isoformat()}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "uuid": "f494ad89-039d-478e-91f2-a63566554666",
                "name": "Fake Corp With Addrs",
                "path": [],
                "attrs": [],
            }
        ]
    }

    query = "social"
    response = service_client.get(
        f"/service/ou/autocomplete/?query={query}&at={at.isoformat()}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "uuid": "68c5d78e-ae26-441f-a143-0103eca8b62a",
                "name": "Social og sundhed",
                "path": ["Overordnet Enhed", "Social og sundhed"],
                "attrs": [],
            },
            {
                "uuid": "5942ce50-2be8-476f-914b-6769a888a7c8",
                "name": "Social og sundhed",
                "path": ["Lønorganisation", "Social og sundhed"],
                "attrs": [],
            },
        ]
    }


@pytest.mark.xfail
@pytest.mark.integration_test
@freezegun.freeze_time("2017-01-01", tz_offset=1)
@pytest.mark.usefixtures("load_fixture_data_with_reset")
def test_v2_search_orgunit_by_name_with_custom_fields(
    mock_get_settings_custom_attrs, service_client: TestClient
):
    at = datetime.now().date()
    query = "Fake Corp"
    response = service_client.get(
        f"/service/ou/autocomplete/?query={query}&at={at.isoformat()}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "uuid": "f494ad89-039d-478e-91f2-a63566554666",
                "name": "Fake Corp With Addrs",
                "path": [],
                "attrs": [
                    {
                        "title": "Afdelingskode",
                        "uuid": "55848eca-4e9e-4f30-954b-78d55eec0441",
                        "value": "Fake afdelingskode",
                    }
                ],
            }
        ]
    }


@pytest.mark.xfail
@pytest.mark.integration_test
@freezegun.freeze_time("2017-01-01", tz_offset=1)
@pytest.mark.usefixtures("load_fixture_data_with_reset")
def test_v2_search_orgunit_by_addr_afdelingskode(
    mock_get_settings_custom_attrs, service_client: TestClient
):
    at = datetime.now().date()
    query = "Fake afdelingskode"
    response = service_client.get(
        f"/service/ou/autocomplete/?query={query}&at={at.isoformat()}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "uuid": "f494ad89-039d-478e-91f2-a63566554666",
                "name": "Fake Corp With Addrs",
                "path": [],
                "attrs": [
                    {
                        "title": "Afdelingskode",
                        "uuid": "55848eca-4e9e-4f30-954b-78d55eec0441",
                        "value": "Fake afdelingskode",
                    }
                ],
            }
        ]
    }


@pytest.mark.xfail
@pytest.mark.integration_test
@freezegun.freeze_time("2017-01-01", tz_offset=1)
@pytest.mark.usefixtures("load_fixture_data_with_reset")
def test_v2_search_orgunit_by_addr_afdelingskode_addr_rename(
    graphapi_post, admin_client, mock_get_settings_custom_attrs
):
    newAddrName = "Fake afdelingskode changed"
    at = datetime.now().date()

    # Modify the addr
    mutate_query = """
    mutation updateAddr($input: AddressUpdateInput!){
        address_update(input: $input) {
            uuid
        }
    }
    """

    payload = jsonable_encoder(
        {
            "uuid": "55848eca-4e9e-4f30-954b-78d55eec0441",
            "value": newAddrName,
            "validity": {"from": at.isoformat()},
            "address_type": "e8ea1a09-d3d4-4203-bfe9-d9a213371337",
        }
    )
    gqlResp: GQLResponse = graphapi_post(mutate_query, {"input": payload})
    assert gqlResp.errors is None
    assert gqlResp.status_code == 200

    # Fetch & assert the orgunit have been renamed accordingly
    query = "Fake afdelingskode"
    response = admin_client.get(
        f"/service/ou/autocomplete/?query={query}&at={at.isoformat()}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "uuid": "f494ad89-039d-478e-91f2-a63566554666",
                "name": "Fake Corp With Addrs",
                "path": [],
                "attrs": [
                    {
                        "title": "Afdelingskode",
                        "uuid": "55848eca-4e9e-4f30-954b-78d55eec0441",
                        "value": newAddrName,
                    }
                ],
            }
        ]
    }
