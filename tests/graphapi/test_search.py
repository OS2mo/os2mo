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

    # Second page: the short final page terminates immediately under keyset
    # pagination, without a trailing empty page.
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

    # Second page: the short final page terminates immediately under keyset
    # pagination, without a trailing empty page.
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
    assert response["page_info"] == {"next_cursor": None}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_employee_query_composes_with_other_filters(
    graphapi_post: GraphAPIPost, create_person: Callable[..., UUID]
) -> None:
    # Both persons share a surname, so `query: "Shared"` matches both.
    persons = [
        create_person({"given_name": "Alice", "surname": "Shared"}),
        create_person({"given_name": "Bob", "surname": "Shared"}),
    ]

    query = """
      query Search($filter: EmployeeFilter) {
        employees(filter: $filter) {
          objects {
            uuid
          }
        }
      }
    """
    # The query filter is AND'ed with the other filters, so restricting by uuid
    # narrows the matches down to a single person.
    response = graphapi_post(
        query, {"filter": {"query": "Shared", "uuids": [str(persons[0])]}}
    )
    assert response.errors is None
    assert response.data is not None
    assert response.data["employees"]["objects"] == [{"uuid": str(persons[0])}]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_org_unit_search_uuid(
    graphapi_post: GraphAPIPost, create_org_unit: Callable[..., UUID]
) -> None:
    ou = str(create_org_unit("random org unit"))

    def search(q: str) -> dict:
        query = """
          query Search($query: String) {
            org_units(filter: {query: $query}) {
              objects {
                current {
                  uuid
                }
              }
            }
          }
        """
        response = graphapi_post(query, {"query": q})
        assert response.errors is None
        assert response.data is not None
        return response.data["org_units"]

    response = search(ou)
    assert response["objects"] == [{"current": {"uuid": ou}}]

    response = search(ou.upper())
    assert response["objects"] == [{"current": {"uuid": ou}}]

    response = search(ou[:10])
    assert response["objects"] == [{"current": {"uuid": ou}}]

    response = search(ou[-10:])
    assert response["objects"] == [{"current": {"uuid": ou}}]

    # Too short to search for UUIDs.
    response = search(ou[:7])
    assert response["objects"] == []
