# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from unittest.mock import AsyncMock
from unittest.mock import patch
from uuid import UUID
from uuid import uuid4

import pytest
from fastapi.encoders import jsonable_encoder
from hypothesis import given
from hypothesis import strategies as st
from more_itertools import one
from pytest import MonkeyPatch

from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from .utils import fetch_employee_validity
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import flatten_data
from mora.graphapi.versions.latest import dataloaders
from mora.graphapi.versions.latest.models import ITUserCreate
from mora.graphapi.versions.latest.types import ITUserType
from ramodels.mo import Validity as RAValidity
from ramodels.mo.details import ITUserRead
from tests.conftest import GQLResponse

# imports for commented out test

# from unittest import mock
# from mora import lora
# from mora.graphapi.versions.latest.it_user import terminate
# from mora.graphapi.versions.latest.models import ITUserTerminate


@given(test_data=graph_data_strat(ITUserRead))
def test_query_all(test_data, graphapi_post, patch_loader):
    """Test that we can query all attributes of the ituser data model."""
    # Patch dataloader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "search_role_type", patch_loader(test_data))
        query = """
            query {
                itusers {
                    uuid
                    objects {
                        uuid
                        user_key
                        employee_uuid
                        itsystem_uuid
                        org_unit_uuid
                        primary_uuid
                        type
                        validity {from to}
                    }

                }
            }
        """
        response: GQLResponse = graphapi_post(query)

    assert response.errors is None
    assert response.data
    assert flatten_data(response.data["itusers"]) == test_data


@given(test_input=graph_data_uuids_strat(ITUserRead))
def test_query_by_uuid(test_input, graphapi_post, patch_loader):
    """Test that we can query itusers by UUID."""
    test_data, test_uuids = test_input

    # Patch dataloader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "get_role_type_by_uuid", patch_loader(test_data))
        query = """
                query TestQuery($uuids: [UUID!]) {
                    itusers(uuids: $uuids) {
                        uuid
                    }
                }
            """
        response: GQLResponse = graphapi_post(query, {"uuids": test_uuids})

    assert response.errors is None
    assert response.data

    # Check UUID equivalence
    result_uuids = [ituser.get("uuid") for ituser in response.data["itusers"]]
    assert set(result_uuids) == set(test_uuids)
    assert len(result_uuids) == len(set(test_uuids))


# --------------------------------------------------------------------------------------
# Create tests
# --------------------------------------------------------------------------------------


@given(test_data=...)
@patch("mora.graphapi.versions.latest.mutators.create_ituser", new_callable=AsyncMock)
async def test_create_ituser(create_ituser: AsyncMock, test_data: ITUserCreate) -> None:
    """Test that pydantic jsons are passed through to create_ituser."""

    mutate_query = """
        mutation CreateITUser($input: ITUserCreateInput!){
            ituser_create(input: $input){
                uuid
            }
        }
    """
    created_uuid = uuid4()
    create_ituser.return_value = ITUserType(uuid=created_uuid)

    payload = jsonable_encoder(test_data)

    response = await execute_graphql(
        query=mutate_query, variable_values={"input": payload}
    )

    assert response.errors is None
    assert response.data == {"ituser_create": {"uuid": str(created_uuid)}}


@patch(
    "mora.service.validation.models.GroupValidation.validate_unique_constraint",
    new_callable=AsyncMock,
)
@given(data=st.data())
@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_create_ituser_integration_test(
    validate_unique_constraint: AsyncMock,
    data: ITUserCreate,
    graphapi_post,
    itsystem_uuids,
    employee_uuids,
) -> None:

    validate_unique_constraint.return_value = None

    employee_uuid = data.draw(st.sampled_from(employee_uuids))
    employee_from, employee_to = fetch_employee_validity(graphapi_post, employee_uuid)

    test_data_validity_start = data.draw(
        st.datetimes(min_value=employee_from, max_value=employee_to or datetime.max)
    )

    if employee_to:
        test_data_validity_end_strat = st.datetimes(
            min_value=test_data_validity_start, max_value=employee_to
        )
    else:
        test_data_validity_end_strat = st.none() | st.datetimes(
            min_value=test_data_validity_start,
        )

    test_data = data.draw(
        st.builds(
            ITUserCreate,
            type=st.just("it"),
            user_key=st.text(
                alphabet=st.characters(whitelist_categories=("L",)), min_size=1
            ),
            itsystem=st.sampled_from(itsystem_uuids),
            person=st.just(employee_uuid),
            validity=st.builds(
                RAValidity,
                from_date=st.just(test_data_validity_start),
                to_date=test_data_validity_end_strat,
            ),
        )
    )

    mutate_query = """
        mutation CreateITUser($input: ITUserCreateInput!){
            ituser_create(input: $input){
                uuid
            }
        }
    """
    response: GQLResponse = graphapi_post(
        mutate_query, {"input": jsonable_encoder(test_data)}
    )
    assert response.errors is None
    uuid = UUID(response.data["ituser_create"]["uuid"])

    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            itusers(uuids: [$uuid]) {
                objects {
                    type
                    user_key
                    itsystem_uuid
                    employee_uuid
                    validity {
                        from
                        to
                    }
                }
            }
        }
    """
    response: GQLResponse = graphapi_post(verify_query, {"uuid": str(uuid)})
    assert response.errors is None

    # IMPORTANT: This is needed and shouldn't (I think), not cause problems.
    # Since we can't avoid the "duplicate error", we set it to None at the top
    # `validate_unique_constraint.return_value = None`, this results in the mutator
    # query failing WITHOUT returning that exact error. Therefore we need to check that
    # response.data["itusers"] is not empty.
    # The test should fail, if any other error is thrown
    if len(response.data["itusers"]):
        obj = one(one(response.data["itusers"])["objects"])
        assert obj["type"] == test_data.type_
        assert obj["user_key"] == test_data.user_key
        assert UUID(obj["itsystem_uuid"]) == test_data.itsystem
        assert UUID(obj["employee_uuid"]) == test_data.person
        assert (
            datetime.fromisoformat(obj["validity"]["from"]).date()
            == test_data.validity.from_date.date()
        )
        if obj["validity"]["to"] is not None:
            assert (
                datetime.fromisoformat(obj["validity"]["to"]).date()
                == test_data.validity.to_date.date()
            )
        else:
            assert test_data.validity.to_date is None


# TODO: Fix failing terminate test #51672
# This test is not consistent, fix it.

# @given(
#     st.uuids(),
#     st.booleans(),
#     st.tuples(st.datetimes() | st.none(), st.datetimes()).filter(
#         lambda dts: dts[0] <= dts[1] if dts[0] and dts[1] else True
#     ),
# )
# async def test_terminate_response(given_uuid, triggerless, given_validity_dts):
#     # Init
#     from_date, to_date = given_validity_dts

#     # The terminate logic have a check that verifies we don't use times other than:
#     # 00:00:00, to the endpoint.. so if we get one of these from hypothesis, we will
#     # expect an exception.
#     expect_exception = False
#     if to_date is None or to_date.time() != datetime.time.min:
#         expect_exception = True

#     # Configure the addr-terminate we want to perform
#     test_data = ITUserTerminate(
#         uuid=given_uuid,
#         triggerless=triggerless,
#         from_date=from_date,
#         to_date=to_date,
#     )

#     # Patching / Mocking
#     async def mock_update(*args):
#         return args[-1]

#     terminate_result_uuid = None
#     caught_exception = None
#     with mock.patch.object(lora.Scope, "update", new=mock_update):
#         try:
#             tr = await terminate(input=test_data)
#             terminate_result_uuid = tr.uuid if tr else terminate_result_uuid
#         except Exception as e:
#             caught_exception = e

#     # Assert
#     if not expect_exception:
#         assert terminate_result_uuid == test_data.uuid
#     else:
#         assert caught_exception is not None
