# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import uuid
from datetime import datetime
from unittest import TestCase
from unittest.mock import patch

import freezegun
import pytest
from fastapi.testclient import TestClient
from mora.config import Settings
from pytest import MonkeyPatch


@pytest.fixture
def mock_get_settings(monkeypatch: MonkeyPatch):
    def mock():
        return Settings(
            confdb_autocomplete_v2_use_legacy=False,
        )

    monkeypatch.setattr("mora.service.orgunit.config.get_settings", mock)


@pytest.fixture
def mock_get_settings_custom_attrs(monkeypatch: MonkeyPatch):
    def mock():
        return Settings(
            confdb_autocomplete_v2_use_legacy=False,
            confdb_autocomplete_attrs_orgunit=[
                uuid.UUID("e8ea1a09-d3d4-4203-bfe9-d9a213371337"),
            ],
            confdb_autocomplete_attrs_employee=[
                uuid.UUID(
                    "06f95678-166a-455a-a2ab-121a8d92ea23"
                ),  # engagement_type = Ansat
                uuid.UUID(
                    "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0"
                ),  # address_type = Email
                uuid.UUID(
                    "62ec821f-4179-4758-bfdf-134529d186e9"
                ),  # association_type = Medlem
                uuid.UUID(
                    "59c135c9-2b15-41cc-97c8-b5dff7180beb"
                ),  # itsystem = Active Directory
                uuid.UUID("14466fb0-f9de-439c-a6c2-b3262c367da7"),  # itsystem = SAP
            ],
        )

    monkeypatch.setattr("mora.service.orgunit.config.get_settings", mock)


@pytest.mark.integration_test
@freezegun.freeze_time("2017-01-01", tz_offset=1)
@pytest.mark.usefixtures("fixture_db")
def test_v2_search_employee_by_uuid(
    mock_get_settings_custom_attrs, service_client: TestClient
):
    at = datetime.now().date()
    query = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
    response = service_client.request(
        "GET", f"/service/e/autocomplete/?query={query}&at={at.isoformat()}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                "name": "Anders And",
                "attrs": [
                    {
                        "title": "Ansat",
                        "uuid": "d000591f-8705-4324-897a-075e3623f37b",
                        "value": "bvn",
                    },
                    {
                        "title": "Email",
                        "uuid": "fba61e38-b553-47cc-94bf-8c7c3c2a6887",
                        "value": "bruger@example.com",
                    },
                    {
                        "title": "Medlem",
                        "uuid": "c2153d5d-4a2b-492d-a18c-c498f7bb6221",
                        "value": "bvn",
                    },
                    {
                        "title": "Medlem",
                        "uuid": "c89853b8-3da5-4b10-8d87-6ca5b4c9416b",
                        "value": "bvn",
                    },
                    {
                        "title": "SAP",
                        "uuid": "4de484d9-f577-4fe0-965f-2d4be11b348c",
                        "value": "donald",
                    },
                    {
                        "title": "Active Directory",
                        "uuid": "aaa8c495-d7d4-4af1-b33a-f4cb27b82c66",
                        "value": "18d2271a-45c4-406c-a482-04ab12f80881",
                    },
                ],
            }
        ]
    }


@pytest.mark.integration_test
@freezegun.freeze_time("2017-01-01", tz_offset=1)
@pytest.mark.usefixtures("fixture_db")
def test_v2_search_employee_by_name(
    mock_get_settings_custom_attrs, service_client: TestClient
):
    at = datetime.now().date()
    query = "Anders And"
    response = service_client.request(
        "GET", f"/service/e/autocomplete/?query={query}&at={at.isoformat()}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                "name": "Anders And",
                "attrs": [
                    {
                        "title": "Ansat",
                        "uuid": "d000591f-8705-4324-897a-075e3623f37b",
                        "value": "bvn",
                    },
                    {
                        "title": "Email",
                        "uuid": "fba61e38-b553-47cc-94bf-8c7c3c2a6887",
                        "value": "bruger@example.com",
                    },
                    {
                        "title": "Medlem",
                        "uuid": "c2153d5d-4a2b-492d-a18c-c498f7bb6221",
                        "value": "bvn",
                    },
                    {
                        "title": "Medlem",
                        "uuid": "c89853b8-3da5-4b10-8d87-6ca5b4c9416b",
                        "value": "bvn",
                    },
                    {
                        "title": "SAP",
                        "uuid": "4de484d9-f577-4fe0-965f-2d4be11b348c",
                        "value": "donald",
                    },
                    {
                        "title": "Active Directory",
                        "uuid": "aaa8c495-d7d4-4af1-b33a-f4cb27b82c66",
                        "value": "18d2271a-45c4-406c-a482-04ab12f80881",
                    },
                ],
            }
        ]
    }

    query = "erik"
    response = service_client.request(
        "GET", f"/service/e/autocomplete/?query={query}&at={at.isoformat()}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "uuid": "236e0a78-11a0-4ed9-8545-6286bb8611c7",
                "name": "Erik Smidt Hansen",
                "attrs": [
                    {
                        "uuid": "301a906b-ef51-4d5c-9c77-386fb8410459",
                        "title": "Ansat",
                        "value": "bvn",
                    },
                    {
                        "uuid": "d3028e2e-1d7a-48c1-ae01-d4c64e64bbab",
                        "title": "Ansat",
                        "value": "bvn",
                    },
                ],
            }
        ]
    }


@pytest.mark.integration_test
@freezegun.freeze_time("2017-01-01", tz_offset=1)
@pytest.mark.usefixtures("fixture_db")
def test_v2_search_employee_by_itsystem(
    mock_get_settings_custom_attrs, service_client: TestClient
):
    at = datetime.now().date()
    query = "donald"
    response = service_client.request(
        "GET", f"/service/e/autocomplete/?query={query}&at={at.isoformat()}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                "name": "Anders And",
                "attrs": [
                    {
                        "title": "Ansat",
                        "uuid": "d000591f-8705-4324-897a-075e3623f37b",
                        "value": "bvn",
                    },
                    {
                        "title": "Email",
                        "uuid": "fba61e38-b553-47cc-94bf-8c7c3c2a6887",
                        "value": "bruger@example.com",
                    },
                    {
                        "title": "Medlem",
                        "uuid": "c2153d5d-4a2b-492d-a18c-c498f7bb6221",
                        "value": "bvn",
                    },
                    {
                        "title": "Medlem",
                        "uuid": "c89853b8-3da5-4b10-8d87-6ca5b4c9416b",
                        "value": "bvn",
                    },
                    {
                        "title": "SAP",
                        "uuid": "4de484d9-f577-4fe0-965f-2d4be11b348c",
                        "value": "donald",
                    },
                    {
                        "title": "Active Directory",
                        "uuid": "aaa8c495-d7d4-4af1-b33a-f4cb27b82c66",
                        "value": "18d2271a-45c4-406c-a482-04ab12f80881",
                    },
                ],
            }
        ]
    }


@pytest.mark.integration_test
@freezegun.freeze_time("2017-01-01", tz_offset=1)
@pytest.mark.usefixtures("fixture_db")
def test_v2_search_orgunit_by_uuid(mock_get_settings, service_client: TestClient):
    at = datetime.now().date()
    query = "f494ad89-039d-478e-91f2-a63566554666"
    response = service_client.request(
        "GET", f"/service/ou/autocomplete/?query={query}&at={at.isoformat()}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "uuid": "f494ad89-039d-478e-91f2-a63566554666",
                "name": "Fake Corp With Addrs",
                "path": [],
                "attrs": [],
                "validity": {"from": "2016-01-01T00:00:00+01:00", "to": None},
            }
        ]
    }

    query = "b688513d-11f7-4efc-b679-ab082a2055d0"
    response = service_client.request(
        "GET", f"/service/ou/autocomplete/?query={query}&at={at.isoformat()}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
                "name": "Samfundsvidenskabelige fakultet",
                "path": ["Overordnet Enhed", "Samfundsvidenskabelige fakultet"],
                "attrs": [],
                "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
            }
        ]
    }


@pytest.mark.integration_test
@freezegun.freeze_time("2017-01-01", tz_offset=1)
@pytest.mark.usefixtures("fixture_db")
def test_v2_search_orgunit_by_name(mock_get_settings, service_client: TestClient):
    at = datetime.now().date()
    query = "Fake Corp"
    response = service_client.request(
        "GET", f"/service/ou/autocomplete/?query={query}&at={at.isoformat()}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "uuid": "f494ad89-039d-478e-91f2-a63566554666",
                "name": "Fake Corp With Addrs",
                "path": [],
                "attrs": [],
                "validity": {"from": "2016-01-01T00:00:00+01:00", "to": None},
            }
        ]
    }

    query = "social"
    response = service_client.request(
        "GET", f"/service/ou/autocomplete/?query={query}&at={at.isoformat()}"
    )

    assert response.status_code == 200
    TestCase().assertCountEqual(
        response.json()["items"],
        [
            {
                "uuid": "68c5d78e-ae26-441f-a143-0103eca8b62a",
                "name": "Social og sundhed",
                "path": ["Overordnet Enhed", "Social og sundhed"],
                "attrs": [],
                "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
            },
            {
                "uuid": "5942ce50-2be8-476f-914b-6769a888a7c8",
                "name": "Social og sundhed",
                "path": ["Lønorganisation", "Social og sundhed"],
                "attrs": [],
                "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
            },
        ],
    )


@pytest.mark.integration_test
@freezegun.freeze_time("2017-01-01", tz_offset=1)
@pytest.mark.usefixtures("fixture_db")
def test_v2_search_orgunit_by_name_with_custom_fields(
    mock_get_settings_custom_attrs, service_client: TestClient
):
    at = datetime.now().date()
    query = "Fake Corp"
    response = service_client.request(
        "GET", f"/service/ou/autocomplete/?query={query}&at={at.isoformat()}"
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
                "validity": {"from": "2016-01-01T00:00:00+01:00", "to": None},
            }
        ]
    }


@pytest.mark.integration_test
@freezegun.freeze_time("2017-01-01", tz_offset=1)
@pytest.mark.usefixtures("fixture_db")
@patch("mora.service.orgunit.autocomplete.search_orgunits")
def test_v2_only_gql_decorate_orgunits(
    mock_search_orgunits, mock_get_settings_custom_attrs, service_client: TestClient
):
    """Verifies that GraphQL part of the autocomplete works as intended."""

    mock_search_orgunits.return_value = [
        uuid.UUID("f494ad89-039d-478e-91f2-a63566554666")
    ]

    at = datetime.now().date()
    query = "f494ad89-039d-478e-91f2-a63566554666"
    response = service_client.request(
        "GET", f"/service/ou/autocomplete/?query={query}&at={at.isoformat()}"
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
                        "uuid": "55848eca-4e9e-4f30-954b-78d55eec0441",
                        "title": "Afdelingskode",
                        "value": "Fake afdelingskode",
                    }
                ],
                "validity": {"from": "2016-01-01T00:00:00+01:00", "to": None},
            }
        ]
    }


@pytest.mark.integration_test
@freezegun.freeze_time("2017-01-01", tz_offset=1)
@pytest.mark.usefixtures("fixture_db")
@patch("mora.service.employee.autocomplete.search_employees")
def test_v2_only_gql_decorate_employees(
    mock_search_employees, mock_get_settings_custom_attrs, service_client: TestClient
):
    """Verifies that GraphQL part of the autocomplete works as intended."""
    mock_search_employees.return_value = [
        uuid.UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a")
    ]

    at = datetime.now().date()
    query = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
    response = service_client.request(
        "GET", f"/service/e/autocomplete/?query={query}&at={at.isoformat()}"
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
                        "uuid": "c89853b8-3da5-4b10-8d87-6ca5b4c9416b",
                        "title": "Medlem",
                        "value": "bvn",
                    },
                    {
                        "uuid": "4de484d9-f577-4fe0-965f-2d4be11b348c",
                        "title": "SAP",
                        "value": "donald",
                    },
                    {
                        "uuid": "aaa8c495-d7d4-4af1-b33a-f4cb27b82c66",
                        "title": "Active Directory",
                        "value": "18d2271a-45c4-406c-a482-04ab12f80881",
                    },
                ],
            }
        ]
    }
