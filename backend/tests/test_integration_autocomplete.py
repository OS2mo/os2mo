# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable

import pytest

from tests.conftest import GraphAPIPost

EMPLOYEE_SEARCH_QUERY = """
    query Search($query: String!) {
        employees(filter: {query: $query}) {
            objects {
                uuid
            }
        }
    }
"""


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_employee_address_search_disabled_by_default(
    graphapi_post: GraphAPIPost,
) -> None:
    """Address search should not return results when the flag is disabled."""
    response = graphapi_post(
        EMPLOYEE_SEARCH_QUERY, variables={"query": "bruger@example.com"}
    )
    assert response.errors is None
    uuids = {obj["uuid"] for obj in response.data["employees"]["objects"]}
    # andersand has this email, but address search is off by default
    assert "53181ed2-f1de-4c4a-a8fd-ab358c2c454a" not in uuids


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_employee_address_search_enabled(
    graphapi_post: GraphAPIPost,
    set_settings: Callable[..., None],
) -> None:
    """Address search should return matching employees when the flag is enabled."""
    set_settings(person_address_search_enabled="True")

    # Search for andersand's email
    response = graphapi_post(
        EMPLOYEE_SEARCH_QUERY, variables={"query": "bruger@example.com"}
    )
    assert response.errors is None
    uuids = {obj["uuid"] for obj in response.data["employees"]["objects"]}
    assert "53181ed2-f1de-4c4a-a8fd-ab358c2c454a" in uuids
