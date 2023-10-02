# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest

from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
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
        ("org_units", 9, 0, 7),
        ("org_units", 11, 0, 9),
        ("org_units", 10, 1, 9),
        ("org_units", 10, 9, 3),
        # Related Units
        ("related_units", None, None, 1),
        ("related_units", 0, 0, 0),
        ("related_units", 1, 0, 1),
        # Roles
        ("roles", None, None, 1),
        ("roles", 0, 0, 0),
        ("roles", 1, 0, 1),
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
        query PaginationTestQuery($limit: int, $offset: int) {{
          {resolver}(limit: $limit, offset: $offset) {{
            uuid
          }}
        }}
    """
    variables = dict(limit=limit, offset=offset)
    response = graphapi_post(query, variables, url="/graphql/v4")
    assert response.errors is None
    assert len(response.data[resolver]) == expected_length


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
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
        # Related Units
        ("related_units", 1, 1),
        # Roles
        ("roles", 1, 1),
        ("roles", 10, 1),
        ("roles", 20, 10),
    ],
)
async def test_pagination_out_of_range(
    graphapi_post: GraphAPIPost, resolver: str, limit: int, offset: int
) -> None:
    """Test that out of range pagination returns None."""
    query = f"""
        query PaginationTestQuery($limit: int, $offset: int) {{
          {resolver}(limit: $limit, offset: $offset) {{
            uuid
          }}
        }}
    """
    variables = dict(limit=limit, offset=offset)
    response = graphapi_post(query, variables, url="/graphql/v4")
    assert response.errors is None
    assert response.data[resolver] == []
    assert response.extensions == {
        "__page_out_of_range": True,
    }
