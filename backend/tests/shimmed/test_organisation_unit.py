# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from fastapi.testclient import TestClient
from tests.util import set_get_configuration

org_unit_type_facet = {
    "description": "",
    "user_key": "org_unit_type",
    "uuid": "fc917e7c-fc3b-47c2-8aa5-a0383342a280",
}


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_nonexistent(service_client: TestClient) -> None:
    response = service_client.request(
        "GET", "/service/ou/00000000-0000-0000-0000-000000000000/"
    )
    assert response.status_code == 404


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_nonexistent_at(service_client: TestClient) -> None:
    response = service_client.request(
        "GET",
        "/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/",
        params={"at": "2000-01-01T00:00:00Z"},
    )
    assert response.status_code == 404


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@set_get_configuration("mora.service.shimmed.org_unit.get_configuration")
def test_get(service_client: TestClient) -> None:
    response = service_client.request(
        "GET", "/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/"
    )
    assert response.status_code == 200
    assert response.json() == {
        "name": "Overordnet Enhed",
        "user_key": "root",
        "user_settings": {"orgunit": {}},
        "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
        "validity": {
            "from": "2016-01-01",
            "to": None,
        },
        "org": {
            "name": "Aarhus Universitet",
            "user_key": "AU",
            "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
        },
        "org_unit_level": None,
        "org_unit_type": {
            "example": None,
            "facet": org_unit_type_facet,
            "name": "Afdeling",
            "full_name": "Afdeling",
            "owner": None,
            "scope": None,
            "top_level_facet": org_unit_type_facet,
            "user_key": "afd",
            "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
        },
        "parent": None,
        "time_planning": None,
        "location": "",
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_get_with_counts(service_client: TestClient) -> None:
    response = service_client.request(
        "GET",
        "/service/ou/9d07123e-47ac-4a9a-88c8-da82e3a4bc9e/",
        params={"count": ["engagement", "association"]},
    )
    assert response.status_code == 200
    assert response.json()["engagement_count"] == 3
    assert response.json()["association_count"] == 2


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@set_get_configuration("mora.service.orgunit.get_configuration")
def test_ou_details(service_client: TestClient) -> None:
    response = service_client.request(
        "GET", "/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/details/org_unit"
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            "name": "Overordnet Enhed",
            "user_key": "root",
            "user_settings": {"orgunit": {}},
            "location": "",
            "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
            "org": {
                "name": "Aarhus Universitet",
                "user_key": "AU",
                "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
            },
            "org_unit_hierarchy": None,
            "org_unit_level": None,
            "org_unit_type": {
                "example": None,
                "facet": org_unit_type_facet,
                "name": "Afdeling",
                "full_name": "Afdeling",
                "owner": None,
                "published": "Publiceret",
                "scope": None,
                "top_level_facet": org_unit_type_facet,
                "user_key": "afd",
                "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
            },
            "parent": None,
            "time_planning": None,
            "validity": {
                "from": "2016-01-01",
                "to": None,
            },
        }
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_get_children(service_client: TestClient) -> None:
    response = service_client.request(
        "GET", "/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/children"
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            "child_count": 0,
            "name": "Social og sundhed",
            "user_key": "social-sundhed",
            "uuid": "68c5d78e-ae26-441f-a143-0103eca8b62a",
            "validity": {"from": "2017-01-01", "to": None},
        },
        {
            "child_count": 1,
            "name": "Humanistisk fakultet",
            "user_key": "hum",
            "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            "validity": {"from": "2016-12-31", "to": None},
        },
        {
            "child_count": 0,
            "name": "Samfundsvidenskabelige fakultet",
            "user_key": "samf",
            "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
            "validity": {"from": "2017-01-01", "to": None},
        },
        {
            "child_count": 1,
            "name": "Skole og Børn",
            "user_key": "skole-børn",
            "uuid": "dad7d0ad-c7a9-4a94-969d-464337e31fec",
            "validity": {"from": "2017-01-01", "to": None},
        },
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_get_children_with_counts(service_client: TestClient) -> None:
    response = service_client.request(
        "GET",
        "/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/children",
        params={"count": ["engagement", "association"]},
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            "association_count": 0,
            "child_count": 0,
            "engagement_count": 0,
            "name": "Social og sundhed",
            "user_key": "social-sundhed",
            "uuid": "68c5d78e-ae26-441f-a143-0103eca8b62a",
            "validity": {"from": "2017-01-01", "to": None},
        },
        {
            "association_count": 2,
            "child_count": 1,
            "engagement_count": 3,
            "name": "Humanistisk fakultet",
            "user_key": "hum",
            "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            "validity": {"from": "2016-12-31", "to": None},
        },
        {
            "association_count": 0,
            "child_count": 0,
            "engagement_count": 0,
            "name": "Samfundsvidenskabelige fakultet",
            "user_key": "samf",
            "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
            "validity": {"from": "2017-01-01", "to": None},
        },
        {
            "association_count": 0,
            "child_count": 1,
            "engagement_count": 0,
            "name": "Skole og Børn",
            "user_key": "skole-børn",
            "uuid": "dad7d0ad-c7a9-4a94-969d-464337e31fec",
            "validity": {"from": "2017-01-01", "to": None},
        },
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_no_children(service_client: TestClient) -> None:
    # b688513d-11f7-4efc-b679-ab082a2055d0 samf has no children
    response = service_client.request(
        "GET",
        "/service/ou/b688513d-11f7-4efc-b679-ab082a2055d0/children",
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_get_children_invalid(service_client: TestClient) -> None:
    # Doesn't exist
    response = service_client.request(
        "GET", "/service/ou/00000000-0000-0000-0000-000000000000/children"
    )
    assert response.status_code == 404
    # Is the root org
    response = service_client.request(
        "GET", "/service/ou/456362c4-0ee4-4e5e-a72c-751239745e62/children"
    )
    assert response.status_code == 404


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@set_get_configuration("mora.service.shimmed.org_unit.get_configuration")
def test_read_root(service_client: TestClient) -> None:
    response = service_client.request(
        "GET", "/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/"
    )
    assert response.status_code == 200
    assert response.json() == {
        "location": "",
        "name": "Overordnet Enhed",
        "org": {
            "name": "Aarhus Universitet",
            "user_key": "AU",
            "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
        },
        "time_planning": None,
        "org_unit_level": None,
        "org_unit_type": {
            "example": None,
            "facet": org_unit_type_facet,
            "name": "Afdeling",
            "full_name": "Afdeling",
            "owner": None,
            "scope": None,
            "top_level_facet": org_unit_type_facet,
            "user_key": "afd",
            "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
        },
        "user_settings": {"orgunit": {}},
        "parent": None,
        "user_key": "root",
        "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
        "validity": {
            "from": "2016-01-01",
            "to": None,
        },
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_children_filtered(service_client: TestClient) -> None:
    # When asking for "&org_unit_hierarchy=<uuid>", the result should only
    # contain org units which have an 'opmærkning' with a UUID of '<uuid>'.
    # With the default test database contents, that means nothing should be
    # returned.
    response = service_client.request(
        "GET",
        "/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/children",
        params={"org_unit_hierarchy": "321f1a2f-e185-42ef-a5f3-bebb2c69f1ba"},
    )
    assert response.json() == []


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_create_root_unit_without_org_id(service_client: TestClient) -> None:
    unitid = "00000000-0000-0000-0000-000000000000"
    orgid = "456362c4-0ee4-4e5e-a72c-751239745e62"
    create = service_client.request(
        "POST",
        "/service/ou/create",
        json={
            "name": "Fake Corp",
            "uuid": unitid,
            "user_key": "fakefakefake",
            "time_planning": None,
            "org_unit_type": {
                "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
            },
            "validity": {
                "from": "2017-01-01",
                "to": None,
            },
        },
    )
    assert create.status_code == 201
    assert create.json() == unitid

    read = service_client.request("GET", f"/service/ou/{unitid}/")
    assert read.status_code == 200
    expected_parent = None
    actual_parent = read.json().get("parent")
    assert expected_parent == actual_parent

    org_children = service_client.request("GET", f"/service/o/{orgid}/children")
    assert {
        "child_count": 0,
        "name": "Fake Corp",
        "user_key": "fakefakefake",
        "uuid": unitid,
        "validity": {
            "from": "2017-01-01",
            "to": None,
        },
    } in org_children.json()
