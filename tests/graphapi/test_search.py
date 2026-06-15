# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from uuid import UUID

import pytest

from ..conftest import GraphAPIPost


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
