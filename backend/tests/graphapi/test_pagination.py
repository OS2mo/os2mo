# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from mora.graphapi.versions.latest.types import Cursor
from mora.util import now

from tests.conftest import GraphAPIPost

serialize_cursor = Cursor._scalar_definition.serialize


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "resolver,limit,offset,expected_length",
    [
        # Addresses
        ("addresses", None, None, 10),
        ("addresses", 0, 0, 0),
        ("addresses", 8, 0, 8),
        ("addresses", 4, 0, 4),
        ("addresses", 8, 1, 8),
        # Associations
        ("associations", None, None, 2),
        ("associations", 0, 0, 0),
        ("associations", 1, 0, 1),
        # Classes
        ("classes", None, None, 39),
        ("classes", 0, 0, 0),
        ("classes", 38, 0, 38),
        ("classes", 10, 0, 10),
        ("classes", 38, 1, 38),
        # Employees
        ("employees", None, None, 5),
        ("employees", 0, 0, 0),
        ("employees", 4, 0, 4),
        ("employees", 2, 0, 2),
        ("employees", 4, 2, 3),
        # Engagements
        ("engagements", None, None, 3),
        ("engagements", 0, 0, 0),
        ("engagements", 3, 0, 3),
        ("engagements", 2, 0, 2),
        ("engagements", 3, 1, 2),
        # Facets
        ("facets", None, None, 18),
        ("facets", 0, 0, 0),
        ("facets", 18, 0, 18),
        ("facets", 10, 0, 10),
        # It Systems
        ("itsystems", None, None, 3),
        ("itsystems", 0, 0, 0),
        ("itsystems", 3, 0, 3),
        ("itsystems", 2, 0, 2),
        ("itsystems", 3, 1, 2),
        # It Users
        ("itusers", None, None, 2),
        ("itusers", 0, 0, 0),
        ("itusers", 1, 0, 1),
        # KLEs
        ("kles", None, None, 1),
        ("kles", 0, 0, 0),
        ("kles", 1, 0, 1),
        # Leaves
        ("leaves", None, None, 2),
        ("leaves", 0, 0, 0),
        ("leaves", 1, 0, 1),
        # Managers
        ("managers", None, None, 1),
        ("managers", 0, 0, 0),
        ("managers", 1, 0, 1),
        # Org Units
        ("org_units", None, None, 10),
        ("org_units", 0, 0, 0),
        # While OFFSET and LIMITing is done in LoRa/SQL, further filtering is sometimes
        # applied in MO. Confusingly, this means that receiving a list shorter than the
        # requested limit does not imply that we are at the end.
        ("org_units", 9, 0, 9),
        ("org_units", 11, 0, 10),
        ("org_units", 10, 1, 9),
        ("org_units", 10, 9, 1),
        # Owners
        ("owners", None, None, 2),
        ("owners", 0, 0, 0),
        ("owners", 1, 0, 1),
        # Related Units
        ("related_units", None, None, 1),
        ("related_units", 0, 0, 0),
        ("related_units", 1, 0, 1),
        # Rolebindings
        ("rolebindings", None, None, 1),
        ("rolebindings", 0, 0, 0),
        ("rolebindings", 1, 0, 1),
    ],
)
async def test_pagination(
    graphapi_post: GraphAPIPost,
    resolver: str,
    limit: int,
    offset: int,
    expected_length: int,
) -> None:
    """Test pagination."""
    query = f"""
        query PaginationTestQuery($limit: int, $cursor: Cursor) {{
          {resolver}(limit: $limit, cursor: $cursor) {{
            objects {{
                uuid
            }}
            page_info {{
                next_cursor
            }}
          }}
        }}
    """
    cursor = None
    if offset is not None:
        cursor = serialize_cursor(Cursor(offset=offset, registration_time=now()))
    variables = dict(limit=limit, cursor=cursor)
    response = graphapi_post(query, variables)
    assert response.errors is None
    assert len(response.data[resolver]["objects"]) == expected_length


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "resolver,limit,offset",
    [
        # Addresses
        ("addresses", 10, 10),
        # Associations
        ("associations", 10, 2),
        # Classes
        ("classes", 42, 41),
        # Employees
        ("employees", 10, 5),
        # Engagements
        ("engagements", 10, 3),
        # Facets
        ("facets", 20, 19),
        # It Systems
        ("itsystems", 10, 3),
        # It Users
        ("itusers", 10, 2),
        # KLEs
        ("kles", 10, 1),
        # Leaves
        ("leaves", 10, 2),
        # Managers
        ("managers", 10, 1),
        # Org Units
        ("org_units", 1, 20),
        # Owners
        ("owners", 1, 2),
        ("owners", 10, 2),
        ("owners", 20, 2),
        # Related Units
        ("related_units", 1, 1),
        # Rolebindings
        ("rolebindings", 1, 1),
        ("rolebindings", 10, 1),
        ("rolebindings", 20, 10),
    ],
)
async def test_pagination_out_of_range(
    graphapi_post: GraphAPIPost, resolver: str, limit: int, offset: int
) -> None:
    """Test that out of range pagination returns None."""
    query = f"""
        query PaginationTestQuery($limit: int, $cursor: Cursor) {{
          {resolver}(limit: $limit, cursor: $cursor) {{
            objects {{
                uuid
            }}
            page_info {{
                next_cursor
            }}
          }}
        }}
    """
    cursor = None
    if offset is not None:
        cursor = serialize_cursor(Cursor(offset=offset, registration_time=now()))
    variables = dict(limit=limit, cursor=cursor)
    response = graphapi_post(query, variables)
    assert response.errors is None
    assert response.data[resolver]["objects"] == []
    assert response.data[resolver]["page_info"]["next_cursor"] is None
    assert response.extensions == {
        "__page_out_of_range": True,
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize("limit", [1, 5, 10, 100])
@pytest.mark.parametrize(
    "resolver,expected",
    [
        ("addresses", 10),
        ("associations", 2),
        ("classes", 39),
        ("employees", 5),
        ("engagements", 3),
        ("facets", 18),
        ("itsystems", 3),
        ("itusers", 2),
        ("kles", 1),
        ("leaves", 2),
        ("managers", 1),
        ("org_units", 10),
        ("owners", 2),
        ("related_units", 1),
        ("rolebindings", 1),
    ],
)
async def test_cursor_based_pagination(
    graphapi_post: GraphAPIPost,
    limit: int,
    resolver: str,
    expected: int,
) -> None:
    """Test that out of range pagination returns None."""
    query = f"""
        query PaginationTestQuery($limit: int, $cursor: Cursor) {{
          {resolver}(limit: $limit, cursor: $cursor) {{
            objects {{
                uuid
            }}
            page_info {{
                next_cursor
            }}
          }}
        }}
    """
    elements = []

    cursor = None
    while True:
        variables = dict(limit=limit, cursor=cursor)
        response = graphapi_post(query, variables)
        assert response.errors is None
        elements.extend(response.data[resolver]["objects"])
        cursor = response.data[resolver]["page_info"]["next_cursor"]
        if cursor is None:
            break

    assert len(elements) == expected
    assert response.extensions == {
        "__page_out_of_range": True,
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_cursor_stable_registration(
    graphapi_post: GraphAPIPost,
) -> None:
    """Test that pagination results in a consistent view."""
    query = """
        query PaginationTestQuery($limit: int, $cursor: Cursor) {
          facets(limit: $limit, cursor: $cursor) {
            objects {
                uuid
            }
            page_info {
                next_cursor
            }
          }
        }
    """
    create_facet_query = """
        mutation CreateFacet($input: FacetCreateInput!) {
          facet_create(input: $input) {
            uuid
          }
        }
    """

    def fetch(cursor):
        variables = dict(limit=5, cursor=cursor)
        response = graphapi_post(query, variables)
        assert response.errors is None
        uuids = {obj["uuid"] for obj in response.data["facets"]["objects"]}
        cursor = response.data["facets"]["page_info"]["next_cursor"]
        return uuids, cursor

    # First, get all facet uuids and store them in original
    original = set()
    cursor = None
    while True:
        uuids, cursor = fetch(cursor)
        original |= uuids
        if cursor is None:
            break

    # Start new pagination, but don't finish
    stable_pagination_result, stable_pagination_cursor = fetch(cursor)
    assert stable_pagination_cursor is not None

    # Add new facet
    response = graphapi_post(
        create_facet_query,
        {
            "input": {
                "user_key": "TestFacet",
                "validity": {
                    "from": now().date().isoformat(),
                    "to": None,
                },
            }
        },
    )
    assert response.errors is None
    new_uuid = response.data["facet_create"]["uuid"]

    # Do yet another fresh pagination, this time we expect the "original" uuids
    # _and_ the `new_uuid`
    final_facets = set()
    cursor = None
    while True:
        uuids, cursor = fetch(cursor)
        final_facets |= uuids
        if cursor is None:
            break
    assert final_facets - original == {
        new_uuid,
    }

    # Finish the "stable" pagination, where we do not expect the new facet
    while True:
        uuids, stable_pagination_cursor = fetch(stable_pagination_cursor)
        stable_pagination_result |= uuids
        if stable_pagination_cursor is None:
            break
    assert original == stable_pagination_result
