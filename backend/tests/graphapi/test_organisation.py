# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from itertools import chain
from typing import Any
from typing import Dict
from typing import Generator
from typing import Optional
from uuid import UUID
from uuid import uuid4

import pytest
from httpx import Response
from more_itertools import distinct_permutations
from more_itertools import one

from .util import execute
from mora.service.org import ConfiguredOrganisation
from mora.service.org import get_configured_organisation


def gen_organisation(
    uuid: Optional[UUID] = None,
    name: str = "name",
    user_key: str = "user_key",
) -> Dict[str, Any]:
    uuid = uuid or uuid4()
    organisation = {
        "id": str(uuid),
        "registreringer": [
            {
                "attributter": {
                    "organisationegenskaber": [
                        {
                            "brugervendtnoegle": user_key,
                            "organisationsnavn": name,
                        }
                    ]
                },
                "tilstande": {"organisationgyldighed": [{"gyldighed": "Aktiv"}]},
            }
        ],
    }
    return organisation


@pytest.fixture
def mock_organisation(respx_mock) -> Generator[UUID, None, None]:
    # Clear Organisation cache before mocking a new one
    ConfiguredOrganisation.clear()

    organisation = gen_organisation()

    respx_mock.get(
        "http://mox/organisation/organisation",
    ).mock(return_value=Response(200, json={"results": [[organisation]]}))
    yield organisation["id"]


@pytest.mark.asyncio
async def test_mocking_and_cache_clearing(respx_mock, mock_organisation):
    """Test that we can mock organisation endpoints and avoid caching.

    The purpose of this test is to easily be able to debug mocking / caching issues.
    """
    uuid = mock_organisation
    raw_org = await get_configured_organisation()

    # We expect only one outgoing request to be done
    assert respx_mock.calls.call_count == 1

    assert raw_org == {"uuid": str(uuid), "name": "name", "user_key": "user_key"}


@pytest.mark.asyncio
async def test_query_organisation(respx_mock, mock_organisation):
    """Test that we are able to query our organisation."""
    uuid = mock_organisation

    query = "query { org { uuid, name, user_key }}"
    result = await execute(query)

    # We expect only one outgoing request to be done
    assert respx_mock.calls.call_count == 1

    assert result.errors is None
    assert result.data
    assert result.data["org"] == {
        "uuid": str(uuid),
        "name": "name",
        "user_key": "user_key",
    }


@pytest.mark.asyncio
async def test_invalid_query_no_organisation(respx_mock):
    """Test that we get an error when querying with no organisation."""
    ConfiguredOrganisation.clear()
    respx_mock.get("http://mox/organisation/organisation").mock(
        return_value=Response(200, json={"results": []})
    )

    query = "query { org { uuid, name, user_key }}"
    result = await execute(query)

    # We expect only one outgoing request to be done
    assert respx_mock.calls.call_count == 1

    # We expect one and only one error
    error = one(result.errors)
    assert error.message == ("ErrorCodes.E_ORG_UNCONFIGURED")
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
@pytest.mark.asyncio
async def test_query_all_permutations_of_organisation(
    respx_mock, fields, mock_organisation
):
    """Test all permutations (15) of queries against our organisation.

    We will only check all permutations here, and for all other entity types we will
    just assume that it works as expected.
    """
    uuid = mock_organisation

    # Fields will contain a tuple of field names with atleast 1 element
    combined_fields = ", ".join(fields)
    query = "query { org { %s }}" % combined_fields
    result = await execute(query)

    # We expect only one outgoing request to be done
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


@pytest.mark.asyncio
async def test_non_existing_field_query(respx_mock, mock_organisation):
    """Test that we are able to query our organisation."""
    query = "query { org { uuid, non_existing_field }}"
    result = await execute(query)

    # We expect parsing to have failed, and thus no outgoing request to be done
    assert respx_mock.calls.call_count == 0
    # We expect one and only one error
    error = one(result.errors)
    assert error.message == (
        "Cannot query field 'non_existing_field' on type 'Organisation'."
    )
    assert result.data is None


@pytest.mark.asyncio
async def test_no_fields_query(respx_mock, mock_organisation):
    """Test that we are able to query our organisation."""
    query = "query { org { }}"
    result = await execute(query)

    # We expect parsing to have failed, and thus no outgoing request to be done
    assert respx_mock.calls.call_count == 0
    # We expect one and only one error
    error = one(result.errors)
    assert error.message == ("Syntax Error: Expected Name, found '}'.")
    assert result.data is None
