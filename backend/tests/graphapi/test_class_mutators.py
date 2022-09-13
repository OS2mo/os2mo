# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from uuid import UUID

import pytest
from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st

from mora.graphapi.versions.latest.graphql_utils import PrintableStr
from mora.graphapi.versions.latest.models import ClassCreate
from mora.graphapi.versions.latest.version import LatestGraphQLSchema
from mora.graphapi.versions.latest.version import LatestGraphQLVersion

# --------------------------------------------------------------------------------------
# Class mutator tests
# --------------------------------------------------------------------------------------

OPTIONAL = {
    "published": st.none() | st.from_regex(PrintableStr.regex),
    "scope": st.none() | st.from_regex(PrintableStr.regex),
    "parent_uuid": st.none() | st.uuids(),
    "example": st.none() | st.from_regex(PrintableStr.regex),
    "owner": st.none() | st.uuids(),
}


@st.composite
def write_strat(draw):
    required = {
        "uuid": st.uuids(),
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


def prepare_query_data(test_data, query_response):

    entries_to_remove = OPTIONAL.keys()
    for k in entries_to_remove:
        test_data.pop(k, None)

    td = {k: v for k, v in test_data.items() if v is not None}

    query_dict = (
        query_response.data.get("classes")[0]
        if isinstance(query_response.data, dict)
        else {}
    )
    query = {k: v for k, v in query_dict.items() if k in td.keys()}

    if not test_data["user_key"]:
        test_data["user_key"] = test_data["uuid"]

    return test_data, query


class TestClassMutator:
    @settings(max_examples=5)
    @given(test_data=write_strat())
    async def test_create_class(self, test_data):
        """Test that we can write all attributes of the class data model."""

        mutate_query = """
                        mutation CreateClass($input: ClassCreateInput!){
                            class_create(input: $input){
                                                        uuid
                                                        }
                        }
                        """

        test_data = prepare_mutator_data(test_data)

        mut_response = await LatestGraphQLSchema.get().execute(
            query=mutate_query, variable_values={"input": test_data}
        )

        response_uuid = (
            mut_response.data.get("class_create", {}).get("uuid", {})
            if isinstance(mut_response.data, dict)
            else {}
        )

        """Query data to check that it actually gets written to database"""
        query_query = """query ($uuid: [UUID!]!)
                        {
                            __typename
                            classes(uuids: $uuid)
                            {
                            uuid
                            type
                            org_uuid
                            user_key
                            name
                            facet_uuid
                            }
                        }

                    """

        graphql_version = LatestGraphQLVersion
        context_value = await graphql_version.get_context()

        query_response = await LatestGraphQLSchema.get().execute(
            query=query_query,
            variable_values={"uuid": str(response_uuid)},
            context_value=context_value,
        )

        test_data, query = prepare_query_data(test_data, query_response)

        """Assert response returned by mutation."""
        assert mut_response.errors is None
        assert mut_response.data
        assert response_uuid == test_data["uuid"]

        """Assert response returned by quering data written."""
        assert query_response.errors is None
        assert query == test_data

    """Test exception gets raised if illegal values are entered"""

    @pytest.mark.parametrize(
        "uuid, type_, user_key, name, org_uuid",
        [
            (
                "23d891b5-85aa-4eee-bec7-e84fe21883c5",
                "class",
                "",
                "\x01",
                "8d6c00dd-4be9-4bdb-a558-1f85183cd920",
            ),
            (
                "23d891b5-85aa-4eee-bec7-e84fe21883c5",
                "class",
                "",
                "",
                "8d6c00dd-4be9-4bdb-a558-1f85183cd920",
            ),
        ],
    )
    def test_write_fails(self, uuid, type_, user_key, name, org_uuid):

        with pytest.raises(Exception):
            ClassCreate(uuid, user_key, type_, name, org_uuid)
