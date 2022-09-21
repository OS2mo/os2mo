# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import datetime
from unittest import mock

from hypothesis import given
from hypothesis import strategies as st
from pytest import MonkeyPatch

from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from mora import lora
from mora.graphapi.shim import flatten_data
from mora.graphapi.versions.latest import dataloaders
from mora.graphapi.versions.latest.it_user import terminate
from mora.graphapi.versions.latest.models import ITUserTerminate
from ramodels.mo.details import ITUserRead
from tests.conftest import GQLResponse


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


@given(
    st.uuids(),
    st.booleans(),
    st.tuples(st.datetimes() | st.none(), st.datetimes()).filter(
        lambda dts: dts[0] <= dts[1] if dts[0] and dts[1] else True
    ),
)
async def test_terminate_response(given_uuid, triggerless, given_validity_dts):
    # Init
    from_date, to_date = given_validity_dts

    # The terminate logic have a check that verifies we don't use times other than:
    # 00:00:00, to the endpoint.. so if we get one of these from hypothesis, we will
    # expect an exception.
    expect_exception = False
    if to_date is None or to_date.time() != datetime.time.min:
        expect_exception = True

    # Configure the addr-terminate we want to perform
    test_data = ITUserTerminate(
        uuid=given_uuid,
        triggerless=triggerless,
        from_date=from_date,
        to_date=to_date,
    )

    # Patching / Mocking
    async def mock_update(*args):
        return args[-1]

    terminate_result_uuid = None
    caught_exception = None
    with mock.patch.object(lora.Scope, "update", new=mock_update):
        try:
            tr = await terminate(input=test_data)
            terminate_result_uuid = tr.uuid if tr else terminate_result_uuid
        except Exception as e:
            caught_exception = e

    # Assert
    if not expect_exception:
        assert terminate_result_uuid == test_data.uuid
    else:
        assert caught_exception is not None
