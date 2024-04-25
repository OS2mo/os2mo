# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import AsyncMock
from unittest.mock import patch
from uuid import UUID
from uuid import uuid4

import pytest
from fastapi.encoders import jsonable_encoder
from hypothesis import given
from hypothesis import HealthCheck
from hypothesis import settings
from hypothesis import strategies as st
from more_itertools import one
from strawberry.types import ExecutionResult

from mora import mapping
from mora.graphapi.shim import execute_graphql
from mora.graphapi.versions.latest.graphql_utils import get_uuids
from mora.graphapi.versions.latest.graphql_utils import PrintableStr
from mora.graphapi.versions.v3.version import ClassCreate
from mora.graphapi.versions.v3.version import GraphQLVersion
from tests.conftest import GraphAPIPost

OPTIONAL = {
    "uuid": st.uuids(),
    "published": st.none() | st.from_regex(PrintableStr.regex),
    "scope": st.none() | st.from_regex(PrintableStr.regex),
    "parent_uuid": st.none() | st.uuids(),
    "example": st.none() | st.from_regex(PrintableStr.regex),
    "owner": st.none() | st.uuids(),
}


@st.composite
def write_strat(draw):
    required = {
        "type": st.just("class"),
        "user_key": st.from_regex(PrintableStr.regex),
        "name": st.from_regex(PrintableStr.regex),
        "facet_uuid": st.uuids(),
        "org_uuid": st.uuids(),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=OPTIONAL))
    return st_dict


def prepare_mutator_data(test_data):
    if "type_" in test_data:
        test_data["type"] = test_data.pop("type_")

    """Change UUID types to string."""
    for k, v in test_data.items():
        if type(v) == UUID:
            test_data[k] = str(v)

    return test_data


def prepare_query_data(test_data, query_response: ExecutionResult):
    entries_to_remove = OPTIONAL.keys()
    for k in entries_to_remove:
        test_data.pop(k, None)

    td = {k: v for k, v in test_data.items() if v is not None}

    assert query_response.errors is None
    assert query_response.data is not None
    query_dict = one(query_response.data["classes"])
    query = {k: v for k, v in query_dict.items() if k in td.keys()}

    if not test_data["user_key"]:
        test_data["user_key"] = test_data["uuid"]

    return test_data, query


@settings(
    suppress_health_check=[
        # Running multiple tests on the same database is okay in this instance
        HealthCheck.function_scoped_fixture,
    ],
)
@given(test_data=write_strat())
@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_integration_create_class(
    test_data,
    graphapi_post: GraphAPIPost,
) -> None:
    """Integrationtest for create class mutator."""

    test_data["org_uuid"] = await get_uuids(mapping.ORG, graphapi_post)
    test_data["facet_uuid"] = await get_uuids(mapping.FACETS, graphapi_post)

    mutate_query = """
        mutation CreateClass($input: ClassCreateInput!) {
          class_create(input: $input) {
            uuid
          }
        }
    """

    test_data = prepare_mutator_data(test_data)

    mut_response = graphapi_post(
        query=mutate_query, variables={"input": test_data}, url="/graphql/v3"
    )

    assert mut_response.errors is None
    assert mut_response.data is not None
    response_uuid = mut_response.data["class_create"]["uuid"]
    if "uuid" in test_data:
        assert response_uuid == test_data["uuid"]

    # Query data to check that it actually gets written to database
    query_query = """
        query ReadClassByUUID($uuid: UUID!) {
          classes(uuids: [$uuid]) {
            uuid
            type
            org_uuid
            user_key
            name
            facet_uuid
          }
        }
    """
    query_response = await execute_graphql(
        query=query_query,
        variable_values={"uuid": response_uuid},
        graphql_version=GraphQLVersion,
    )

    test_data, query = prepare_query_data(test_data, query_response)

    # Assert response returned by quering data written
    assert query_response.errors is None
    assert query_response.data is not None
    assert query == test_data


# Test exception gets raised if illegal values are entered


@given(test_data=write_strat())
@patch("mora.graphapi.versions.v3.version.create_class", new_callable=AsyncMock)
async def test_unit_create_class(
    create_class: AsyncMock, test_data: ClassCreate
) -> None:
    """Unit test for create class mutator."""

    mutate_query = """
        mutation CreateClass($input: ClassCreateInput!){
            class_create(input: $input){
                uuid
            }
        }
    """
    if test_data.get("uuid"):
        created_uuid = test_data["uuid"]
    else:
        created_uuid = uuid4()
    create_class.return_value = created_uuid

    payload = jsonable_encoder(test_data)
    response = await execute_graphql(
        query=mutate_query,
        variable_values={"input": payload},
        graphql_version=GraphQLVersion,
    )

    assert response.errors is None
    assert response.data == {"class_create": {"uuid": str(created_uuid)}}
