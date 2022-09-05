# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import datetime
from unittest import mock

from hypothesis import given
from hypothesis import strategies as st
from pytest import MonkeyPatch

import mora.graphapi.dataloaders as dataloaders
from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from mora import lora
from mora.graphapi.engagements import terminate_engagement
from mora.graphapi.models import EngagementTerminate
from mora.graphapi.shim import flatten_data
from ramodels.mo.details import EngagementRead
from tests.conftest import GQLResponse

# import mock as mk

# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------


class TestEngagementsQuery:
    """Class collecting engagements query tests.

    Data loaders are mocked to return specific values, generated via
    Hypothesis.
    MonkeyPatch.context is used as a context manager to achieve this,
    because mocks are *not* reset between invocations of Hypothesis examples.
    """

    @given(test_data=graph_data_strat(EngagementRead))
    def test_query_all(self, test_data, graphapi_post, patch_loader):
        """Test that we can query all attributes of the engagement data model."""
        # Patch dataloader
        with MonkeyPatch.context() as patch:
            patch.setattr(dataloaders, "search_role_type", patch_loader(test_data))
            query = """
                query {
                    engagements {
                        uuid
                        objects {
                            uuid
                            org_unit_uuid
                            employee_uuid
                            engagement_type_uuid
                            job_function_uuid
                            leave_uuid
                            primary_uuid
                            type
                            user_key
                            fraction
                            validity {from to}
                            extension_1
                            extension_2
                            extension_3
                            extension_4
                            extension_5
                            extension_6
                            extension_7
                            extension_8
                            extension_9
                            extension_10
                        }
                    }
                }
            """
            response: GQLResponse = graphapi_post(query)

        assert response.errors is None
        assert response.data
        assert flatten_data(response.data["engagements"]) == test_data

    @given(test_input=graph_data_uuids_strat(EngagementRead))
    def test_query_by_uuid(self, test_input, graphapi_post, patch_loader):
        """Test that we can query engagements by UUID."""
        test_data, test_uuids = test_input

        # Patch dataloader
        with MonkeyPatch.context() as patch:
            patch.setattr(dataloaders, "get_role_type_by_uuid", patch_loader(test_data))
            query = """
                    query TestQuery($uuids: [UUID!]) {
                        engagements(uuids: $uuids) {
                            uuid
                        }
                    }
                """
            response: GQLResponse = graphapi_post(query, {"uuids": test_uuids})

        assert response.errors is None
        assert response.data

        # Check UUID equivalence
        result_uuids = [assoc.get("uuid") for assoc in response.data["engagements"]]
        assert set(result_uuids) == set(test_uuids)
        assert len(result_uuids) == len(set(test_uuids))

    @given(test_data=graph_data_strat(EngagementRead))
    def test_query_is_primary(self, test_data, graphapi_post, patch_loader):
        """Test that we can query 'is_primary' from the engagement data model."""

        query = """
                query {
                    engagements {
                        uuid
                        objects {
                            uuid
                            is_primary
                        }
                    }
                }
            """
        # Patch dataloader
        with MonkeyPatch.context() as patch:
            patch.setattr(dataloaders, "search_role_type", patch_loader(test_data))
            # Patch check for is_primary
            with mock.patch(
                "mora.graphapi.schema.is_class_uuid_primary", return_value=True
            ) as primary_mock:
                response: GQLResponse = graphapi_post(query)

        assert response.errors is None

        for e in response.data["engagements"]:

            if test_data[0]["primary_uuid"]:
                # primary_uuid is optional.
                # If it exists the patched is_primary returns True
                expected = True
                primary_mock.assert_called_once_with(test_data[0]["uuid"])
            else:
                # If primary_uuid is None the check is not done and is_primary is False
                expected = False
                primary_mock.assert_not_called()

            assert e["objects"][0]["is_primary"] == expected


class TestEngagementsTerminate:
    @given(
        st.uuids(),
        st.booleans(),
        st.tuples(st.datetimes() | st.none(), st.datetimes()).filter(
            lambda dts: dts[0] <= dts[1] if dts[0] and dts[1] else True
        ),
    )
    async def test_terminate_response(
        self, given_uuid, triggerless, given_validity_dts
    ):
        # Init
        from_date, to_date = given_validity_dts

        # The terminate logic have a check that verifies we don't use times other than:
        # 00:00:00, to the endpoint.. so if we get one of these from hypothesis, we will
        # expect an exception.
        expect_exception = False
        if to_date is None or to_date.time() != datetime.time.min:
            expect_exception = True

        # Configure the addr-terminate we want to perform
        test_data = EngagementTerminate(
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
                tr = await terminate_engagement(input=test_data)
                terminate_result_uuid = tr.uuid if tr else terminate_result_uuid
            except Exception as e:
                caught_exception = e

        # Assert
        if not expect_exception:
            assert terminate_result_uuid == test_data.uuid
        else:
            assert caught_exception is not None
