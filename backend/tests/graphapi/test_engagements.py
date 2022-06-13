# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from hypothesis import given
from pytest import MonkeyPatch
from ramodels.mo.details import EngagementRead

import mora.graphapi.dataloaders as dataloaders
from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from mora.graphapi.shim import flatten_data
from tests.conftest import GQLResponse

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
