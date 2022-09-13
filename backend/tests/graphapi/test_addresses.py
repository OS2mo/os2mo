# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import asyncio
import datetime
import uuid as uuid_lib
from uuid import UUID
from unittest.mock import patch
from uuid import UUID
from typing import Optional

from fastapi.encoders import jsonable_encoder
from hypothesis import given
from hypothesis import strategies as st
from mock import patch
from pytest import MonkeyPatch
from strawberry.types import ExecutionResult

from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from mora import lora
from mora.graphapi.shim import flatten_data
from mora.graphapi.versions.latest import dataloaders
from mora.graphapi.versions.latest.address import terminate as address_terminate
from mora.graphapi.versions.latest.models import AddressTerminate
from mora.graphapi.versions.latest.version import LatestGraphQLSchema
from ramodels.mo.details import AddressRead
from tests.conftest import GQLResponse


# --------------------------------------------------------------------------------------
# Mocks
# --------------------------------------------------------------------------------------
def async_lora_return(*args):
    """Returns last positional argument using asyncio.Future.

    This is used to mock lora.Scope methods like 'get' and 'update'."""

    f = asyncio.Future()
    f.set_result(args[-1])
    return f


# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------


class TestAddresssQuery:
    """Class collecting addresses query tests.

    Data loaders are mocked to return specific values, generated via
    Hypothesis.
    MonkeyPatch.context is used as a context manager to achieve this,
    because mocks are *not* reset between invocations of Hypothesis examples.
    """

    @given(test_data=graph_data_strat(AddressRead))
    def test_query_all(self, test_data, graphapi_post, patch_loader):
        """Test that we can query all attributes of the address data model."""
        # JSON encode test data
        test_data = jsonable_encoder(test_data)

        # Patch dataloader
        with MonkeyPatch.context() as patch:
            patch.setattr(dataloaders, "search_role_type", patch_loader(test_data))
            query = """
                query {
                    addresses {
                        uuid
                        objects {
                            uuid
                            user_key
                            address_type_uuid
                            employee_uuid
                            org_unit_uuid
                            engagement_uuid
                            visibility_uuid
                            type
                            value
                            value2
                            validity {from to}
                        }
                    }
                }
            """
            response: GQLResponse = graphapi_post(query)

        assert response.errors is None
        assert response.data
        assert flatten_data(response.data["addresses"]) == test_data

    @given(test_input=graph_data_uuids_strat(AddressRead))
    def test_query_by_uuid(self, test_input, graphapi_post, patch_loader):
        """Test that we can query addresses by UUID."""
        test_data, test_uuids = test_input

        # Patch dataloader
        with MonkeyPatch.context() as patch:
            patch.setattr(dataloaders, "get_role_type_by_uuid", patch_loader(test_data))
            query = """
                    query TestQuery($uuids: [UUID!]) {
                        addresses(uuids: $uuids) {
                            uuid
                        }
                    }
                """
            response: GQLResponse = graphapi_post(query, {"uuids": test_uuids})

        assert response.errors is None
        assert response.data

        # Check UUID equivalence
        result_uuids = [addr.get("uuid") for addr in response.data["addresses"]]
        assert set(result_uuids) == set(test_uuids)
        assert len(result_uuids) == len(set(test_uuids))


@given(
    given_uuid=st.uuids(),
    triggerless=st.booleans(),
    given_validity_dts=st.tuples(st.datetimes() | st.none(), st.datetimes()).filter(
        lambda dts: dts[0] <= dts[1] if dts[0] and dts[1] else True
    ),
)
@patch.object(lora.Scope, "update", async_lora_return)
@patch.object(lora.Scope, "get", async_lora_return)
async def test_terminate(given_uuid, triggerless, given_validity_dts):
    from_date, to_date = given_validity_dts

    # The terminate logic have a check that verifies we don't use times other than:
    # 00:00:00, to the endpoint.. so if we get one of these from hypothesis, we will
    # expect an exception.
    expect_exception = False
    if to_date.time() != datetime.time.min:
        expect_exception = True

    # Configure the addr-terminate we want to perform
    at = AddressTerminate(
        uuid=given_uuid,
        triggerless=triggerless,
        from_date=from_date,
        to_date=to_date,
    )

    terminate_result_uuid = None
    caught_exception = None
    try:
        tr = await address_terminate(address_terminate=at)
        terminate_result_uuid = tr.uuid if tr else terminate_result_uuid
    except Exception as e:
        caught_exception = e

    # Assert
    if not expect_exception:
        assert terminate_result_uuid == at.uuid
    else:
        assert caught_exception is not None


@given(
    st.text(),
    st.uuids(),
    st.uuids(),
    st.sampled_from(["org_unit", "person", "engagement"]),
    st.uuids(),
    st.uuids() | st.none(),
    st.tuples(st.datetimes() | st.none(), st.datetimes() | st.none()).filter(
        lambda dts: dts[0] <= dts[1] if dts[0] and dts[1] else True
    ),
)
async def test_create_mutator(
    given_value,
    given_address_type_uuid,
    given_visibility_uuid,
    given_relation_type,
    given_relation_uuid,
    given_org_uuid,
    given_validity_dts,
):
    # Convert the UUIDs to strings, so they can be used in the mutation-query
    given_address_type_uuid = str(given_address_type_uuid)
    given_visibility_uuid = str(given_visibility_uuid)
    given_relation_uuid = str(given_relation_uuid)
    given_org_uuid = str(given_org_uuid) if given_org_uuid else given_org_uuid

    given_validity_from, given_validity_to = given_validity_dts
    given_relation = {
        "type": given_relation_type,
        "uuid": given_relation_uuid,
    }

    # Create GraphQL arguments, starting with the required ones
    var_values = {
        "value": given_value,
        "addressType": given_address_type_uuid,
        "visibility": given_visibility_uuid,
        "relation": given_relation,
        "org": given_org_uuid,
    }

    if given_validity_from:
        var_values["from"] = given_validity_from.date().isoformat()

    if given_validity_to:
        var_values["to"] = given_validity_to.date().isoformat()

    with patch(
        "mora.graphapi.versions.latest.address.handlers.generate_requests"
    ) as mock_generate_requests, patch(
        "mora.graphapi.versions.latest.address.handlers.submit_requests"
    ) as mock_submit_requests:
        mock_generate_requests.return_value = {"test": "request"}
        mock_submit_requests.return_value = [str(uuid_lib.uuid4())]
        # GraphQL
        mutation_func = "address_create"
        query = (
            "mutation($value: String!, $addressType: UUID!, $visibility: UUID!, "
            "$relation: AddressRelationInput!, $from: DateTime, $to: DateTime, "
            "$org: UUID) {"
            f"{mutation_func}(input: {{value: $value, address_type: $addressType, "
            f"visibility: $visibility, relation: $relation, from: $from, to: $to, "
            f"org: $org}})"
            "}"
        )

        response = await LatestGraphQLSchema.get().execute(
            query, variable_values=var_values
        )

        mock_generate_requests.assert_called()
        mock_submit_requests.assert_called_with(mock_generate_requests.return_value)

        new_addr_uuid = (
            response.data.get(mutation_func)
            if isinstance(response, ExecutionResult)
            else None
        )
        assert new_addr_uuid == mock_submit_requests.return_value[0]


@given(
    st.emails(),
    st.uuids(),
    st.uuids(),
    st.sampled_from(["org_unit", "person", "engagement"]),
    st.uuids(),
    st.uuids() | st.none(),
    st.tuples(st.datetimes() | st.none(), st.datetimes() | st.none()).filter(
        lambda dts: dts[0] <= dts[1] if dts[0] and dts[1] else True
    ),
)
@mock.patch.object(lora.Scope, "create", lambda *args: args[-1])
@mock.patch.object(lora.Scope, "get", mock.AsyncMock())
async def test_create_request_handler_logic(
    given_value,
    given_address_type_uuid,
    given_visibility_uuid,
    given_relation_type,
    given_relation_uuid,
    given_org_uuid,
    given_validity_dts,
):
    given_validity_from, given_validity_to = given_validity_dts

    with mock.patch(
        "mora.service.org.get_configured_organisation"
    ) as get_configured_organisation, mock.patch(
        "mora.service.address.facet.get_one_class"
    ) as mock_get_one_class, mock.patch(
        "mora.graphapi.versions.latest.models.AddressCreate._get_org_unit_validity"
    ) as mock_get_org_unit_validity, mock.patch(
        "mora.graphapi.versions.latest.models.AddressCreate._get_person_validity"
    ) as mock_get_person_validity:
        get_configured_organisation.return_value = {"uuid": given_org_uuid}
        mock_get_one_class.return_value = {"scope": "EMAIL"}

        if given_relation_type in ["org_unit", "person"]:
            validity = {
                "from": given_validity_from.date().isoformat(),
                "to": given_validity_from.date().isoformat(),
            }
            mock_get_org_unit_validity.return_value = validity
            mock_get_person_validity.return_value = validity
        else:
            mock_get_org_unit_validity.return_value = None
            mock_get_person_validity.return_value = None

        # Convert the UUIDs to strings, so they can be used in the mutation-query
        given_address_type_uuid = str(given_address_type_uuid)
        given_visibility_uuid = str(given_visibility_uuid)
        given_relation_uuid = str(given_relation_uuid)
        given_org_uuid = str(given_org_uuid) if given_org_uuid else given_org_uuid

        given_relation = {
            "type": given_relation_type,
            "uuid": given_relation_uuid,
        }

        # Create GraphQL arguments, starting with the required ones
        var_values = {
            "value": given_value,
            "addressType": given_address_type_uuid,
            "visibility": given_visibility_uuid,
            "relation": given_relation,
            "org": given_org_uuid,
        }

        if given_validity_from:
            var_values["from"] = given_validity_from.date().isoformat()

        if given_validity_to:
            var_values["to"] = given_validity_to.date().isoformat()

        # GraphQL
        mutation_func = "address_create"
        query = (
            "mutation($value: String!, $addressType: UUID!, $visibility: UUID!, "
            "$relation: AddressRelationInput!, $from: DateTime, $to: DateTime, "
            "$org: UUID) {"
            f"{mutation_func}(input: {{value: $value, address_type: $addressType, "
            f"visibility: $visibility, relation: $relation, from: $from, to: $to, "
            f"org: $org}})"
            "}"
        )

        response = await LatestGraphQLSchema.get().execute(
            query, variable_values=var_values
        )
        tap = "test"
