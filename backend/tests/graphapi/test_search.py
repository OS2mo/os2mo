# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from uuid import UUID

import pytest

from ..conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_employee_pagination(
    graphapi_post: GraphAPIPost, create_person: Callable[..., UUID]
) -> None:
    # Create persons
    persons = [
        str(create_person()),
        str(create_person()),
        str(create_person()),
    ]
    persons.sort()  # persons are created with random uuids

    # Search
    def search(variables: dict) -> dict:
        query = """
          query Search($filter: EmployeeFilter, $limit: int, $cursor: Cursor) {
            employees(filter: $filter, limit: $limit, cursor: $cursor) {
              objects {
                current {
                  uuid
                }
              }
              page_info {
                next_cursor
              }
            }
          }
        """
        response = graphapi_post(query, variables)
        assert response.errors is None
        assert response.data is not None
        return response.data["employees"]

    # First page
    response = search(
        {
            "filter": {"query": "4"},
            "limit": 2,
            "cursor": None,
        }
    )
    assert response["objects"] == [
        {"current": {"uuid": persons[0]}},
        {"current": {"uuid": persons[1]}},
    ]

    # Second page
    response = search(
        {
            "filter": {"query": "4"},
            "limit": 2,
            "cursor": response["page_info"]["next_cursor"],
        }
    )
    assert response["objects"] == [
        {"current": {"uuid": persons[2]}},
    ]

    # Third page
    response = search(
        {
            "filter": {"query": "4"},
            "limit": 2,
            "cursor": response["page_info"]["next_cursor"],
        }
    )
    assert response["objects"] == []
    assert response["page_info"] == {"next_cursor": None}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_org_unit_pagination(
    graphapi_post: GraphAPIPost, create_org_unit: Callable[..., UUID]
) -> None:
    # Create units
    units = [
        str(create_org_unit("foo")),
        str(create_org_unit("foo")),
        str(create_org_unit("foo")),
    ]
    units.sort()  # units are created with random uuids

    # Search
    def search(variables: dict) -> dict:
        query = """
          query Search($filter: OrganisationUnitFilter, $limit: int, $cursor: Cursor) {
            org_units(filter: $filter, limit: $limit, cursor: $cursor) {
              objects {
                current {
                  uuid
                }
              }
              page_info {
                next_cursor
              }
            }
          }
        """
        response = graphapi_post(query, variables)
        assert response.errors is None
        assert response.data is not None
        return response.data["org_units"]

    # First page
    response = search(
        {
            "filter": {"query": "foo"},
            "limit": 2,
            "cursor": None,
        }
    )
    assert response["objects"] == [
        {"current": {"uuid": units[0]}},
        {"current": {"uuid": units[1]}},
    ]

    # Second page
    response = search(
        {
            "filter": {"query": "foo"},
            "limit": 2,
            "cursor": response["page_info"]["next_cursor"],
        }
    )
    assert response["objects"] == [
        {"current": {"uuid": units[2]}},
    ]

    # Third page
    response = search(
        {
            "filter": {"query": "foo"},
            "limit": 2,
            "cursor": response["page_info"]["next_cursor"],
        }
    )
    assert response["objects"] == []
    assert response["page_info"] == {"next_cursor": None}
