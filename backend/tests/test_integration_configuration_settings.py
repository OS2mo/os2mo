# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from fastapi.testclient import TestClient
from mora.config import NavLink
from mora.config import Settings

from tests import util


def test_global_user_settings_read(service_client: TestClient) -> None:
    """Test that it is possible to correctly read default global settings."""
    url = "/service/configuration"
    response = service_client.request("GET", url)
    assert response.status_code == 200
    user_settings = response.json()
    assert "show_location" in user_settings
    assert "show_user_key" in user_settings
    assert "show_roles" in user_settings
    assert user_settings["show_location"] is True


def test_global_user_settings_write(service_client: TestClient) -> None:
    """Test that it is no longer possible to write a global setting."""
    url = "/service/configuration"
    payload = {"org_units": {"show_roles": "False"}}
    response = service_client.request("POST", url, json=payload)
    assert response.status_code == 410

    response = service_client.request("GET", url)
    assert response.status_code == 200
    user_settings = response.json()
    assert user_settings["show_roles"] is True

    payload = {"org_units": {"show_roles": "True"}}
    response = service_client.request("POST", url, json=payload)
    assert response.status_code == 410

    response = service_client.request("GET", url)
    assert response.status_code == 200
    user_settings = response.json()
    assert user_settings["show_roles"] is True


def test_ou_user_settings(service_client: TestClient) -> None:
    """Test that reading and writing settings on units works corrcectly."""
    uuid = "b688513d-11f7-4efc-b679-ab082a2055d0"
    url = f"/service/ou/{uuid}/configuration"
    payload = {"org_units": {"show_user_key": "True"}}
    response = service_client.request("POST", url, json=payload)
    assert response.status_code == 410

    response = service_client.request("GET", url)
    assert response.status_code == 200
    assert "show_kle" in response.json()


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_ou_service_response(service_client: TestClient) -> None:
    """
    Test that the service endpoint for units returns the correct
    configuration settings, including that this endpoint should convert
    the magic strings 'True' and 'False' into boolean values.
    """
    uuid = "b688513d-11f7-4efc-b679-ab082a2055d0"

    url = f"/service/ou/{uuid}/configuration"
    payload = {"org_units": {"show_user_key": "True"}}
    response = service_client.request("POST", url, json=payload)
    assert response.status_code == 410

    payload = {"org_units": {"show_location": "False"}}
    response = service_client.request("POST", url, json=payload)
    assert response.status_code == 410

    response = service_client.request("GET", f"/service/ou/{uuid}/")
    assert response.status_code == 200
    result = response.json()
    user_settings = result["user_settings"]["orgunit"]
    assert user_settings["show_user_key"]
    assert user_settings["show_location"]


def test_empty_list(service_client: TestClient) -> None:
    url = "/service/navlinks"
    response = service_client.request("GET", url)
    assert response.status_code == 200
    assert response.json() == [{}]


async def test_populated_list(service_client: TestClient) -> None:
    url = "/service/navlinks"
    href = "http://google.com"
    text = "Google"

    with util.override_config(Settings(navlinks=[NavLink(href=href, text=text)])):
        response = service_client.request("GET", url)
        assert response.status_code == 200
        assert response.json() == [{"href": "http://google.com", "text": "Google"}]
