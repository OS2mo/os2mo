# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from itertools import chain
from unittest.mock import AsyncMock

import pytest
from mora.service.org import get_configured_organisation
from more_itertools import distinct_permutations
from more_itertools import one
from oio_rest.organisation import Organisation

from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost


async def test_mocking_and_cache_clearing(mock_organisation):
    """Test that we can mock organisation endpoints and avoid caching.

    The purpose of this test is to easily be able to debug mocking / caching issues.
    """
    uuid = mock_organisation
    raw_org = await get_configured_organisation()
    assert raw_org == {"uuid": str(uuid), "name": "name", "user_key": "user_key"}


def test_query_organisation(graphapi_post: GraphAPIPost, mock_organisation):
    """Test that we are able to query our organisation."""
    uuid = mock_organisation

    query = "query { org { uuid, name, user_key }}"
    result: GQLResponse = graphapi_post(query)

    assert result.errors is None
    assert result.data
    assert result.data["org"] == {
        "uuid": str(uuid),
        "name": "name",
        "user_key": "user_key",
    }


async def test_invalid_query_no_organisation(graphapi_post: GraphAPIPost, monkeypatch):
    """Test that we get an error when querying with no organisation."""
    monkeypatch.setattr(
        Organisation, "get_objects_direct", AsyncMock(return_value={"results": []})
    )

    query = "query { org { uuid, name, user_key }}"
    result: GQLResponse = graphapi_post(query)

    # We expect one and only one error
    error = one(result.errors)
    assert error["message"] == "ErrorCodes.E_ORG_UNCONFIGURED"
    assert result.data is None


org_fields = ["uuid", "name", "user_key"]


@pytest.mark.parametrize(
    "fields",
    sorted(
        chain(
            distinct_permutations(org_fields, 1),  # 3 (3) permutations
            distinct_permutations(org_fields, 2),  # 6 (3 * 2) permutations
            distinct_permutations(org_fields, 3),  # 6 (3 * 2 * 1) permutations
        )
    ),
)
async def test_query_all_permutations_of_organisation(
    graphapi_post: GraphAPIPost, respx_mock, fields, mock_organisation
):
    """Test all permutations (15) of queries against our organisation.

    We will only check all permutations here, and for all other entity types we will
    just assume that it works as expected.
    """
    uuid = mock_organisation

    # Fields will contain a tuple of field names with atleast 1 element
    combined_fields = ", ".join(fields)
    query = "query { org { %s }}" % combined_fields
    result: GQLResponse = graphapi_post(query)

    # We expect only expect the GraphQL request.
    assert respx_mock.calls.call_count == 1

    assert result.errors is None
    # Check that all expected fields are in output
    assert result.data
    org = result.data["org"]
    if "uuid" in fields:
        assert org.pop("uuid") == str(uuid)
    if "name" in fields:
        assert org.pop("name") == "name"
    if "user_key" in fields:
        assert org.pop("user_key") == "user_key"
    # Check that no extra fields were returned
    assert org == {}


async def test_non_existing_field_query(graphapi_post: GraphAPIPost, respx_mock):
    """Test that we are able to query our organisation."""
    query = "query { org { uuid, non_existing_field }}"
    result: GQLResponse = graphapi_post(query)

    # We expect parsing to have failed, and thus only one outgoing request to be done;
    # the GraphQL query itself, but no call to the underlying LoRa
    assert respx_mock.calls.call_count == 1
    # We expect one and only one error
    error = one(result.errors)
    assert error["message"] == (
        "Cannot query field 'non_existing_field' on type 'Organisation'."
    )
    assert result.data is None


async def test_no_fields_query(graphapi_post: GraphAPIPost, respx_mock):
    """Test that we are able to query our organisation."""
    query = "query { org { }}"
    result: GQLResponse = graphapi_post(query)

    # We expect parsing to have failed, and thus only one outgoing request to be done;
    # the GraphQL query itself, but no call to the underlying LoRa
    assert respx_mock.calls.call_count == 1
    # We expect one and only one error
    error = one(result.errors)
    assert error["message"] == "Syntax Error: Expected Name, found '}'."
    assert result.data is None
