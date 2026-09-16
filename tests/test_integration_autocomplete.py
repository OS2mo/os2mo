# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

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
@pytest.mark.envvar({"PERSON_ADDRESS_SEARCH_ENABLED": "True"})
@pytest.mark.usefixtures("fixture_db")
def test_employee_address_search_enabled(
    graphapi_post: GraphAPIPost,
) -> None:
    """Address search should return matching employees when the flag is enabled."""
    # Search for andersand's email
    response = graphapi_post(
        EMPLOYEE_SEARCH_QUERY, variables={"query": "bruger@example.com"}
    )
    assert response.errors is None
    uuids = {obj["uuid"] for obj in response.data["employees"]["objects"]}
    assert "53181ed2-f1de-4c4a-a8fd-ab358c2c454a" in uuids


@pytest.mark.integration_test
@pytest.mark.envvar({"PERSON_ADDRESS_SEARCH_ENABLED": "True"})
@pytest.mark.usefixtures("fixture_db")
def test_employee_address_search_phone(
    graphapi_post: GraphAPIPost,
) -> None:
    """Address search should also find employees by phone number."""
    response = graphapi_post(EMPLOYEE_SEARCH_QUERY, variables={"query": "20304060"})
    assert response.errors is None
    uuids = {obj["uuid"] for obj in response.data["employees"]["objects"]}
    assert "53181ed2-f1de-4c4a-a8fd-ab358c2c454a" in uuids


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_employee_cpr_search_enabled(
    graphapi_post: GraphAPIPost,
) -> None:
    """CPR search should return matching employees by default."""
    response = graphapi_post(EMPLOYEE_SEARCH_QUERY, variables={"query": "0906340000"})
    assert response.errors is None
    uuids = {obj["uuid"] for obj in response.data["employees"]["objects"]}
    assert "53181ed2-f1de-4c4a-a8fd-ab358c2c454a" in uuids


@pytest.mark.integration_test
@pytest.mark.envvar({"PERSON_CPR_SEARCH_ENABLED": "False"})
@pytest.mark.usefixtures("fixture_db")
def test_employee_cpr_search_disabled(
    graphapi_post: GraphAPIPost,
) -> None:
    """CPR search should not return results when the flag is disabled."""
    response = graphapi_post(EMPLOYEE_SEARCH_QUERY, variables={"query": "0906340000"})
    assert response.errors is None
    uuids = {obj["uuid"] for obj in response.data["employees"]["objects"]}
    assert "53181ed2-f1de-4c4a-a8fd-ab358c2c454a" not in uuids
