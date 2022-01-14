# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from fastapi.encoders import jsonable_encoder
from hypothesis import given
from hypothesis import strategies as st
from pytest import MonkeyPatch
from ramodels.mo.details import EngagementRead

import mora.graphapi.dataloaders as dataloaders
from mora.graphapi.main import get_schema

# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------

SCHEMA = str(get_schema())


class TestEngagementsQuery:
    """Class collecting engagements query tests.

    Data loaders are mocked to return specific values, generated via
    Hypothesis.
    MonkeyPatch.context is used as a context manager to achieve this,
    because mocks are *not* reset between invocations of Hypothesis examples.
    """

    @given(test_data=st.lists(st.builds(EngagementRead)))
    def test_query_all(self, test_data, graphapi_test, patch_loader):
        """Test that we can query all attributes of the engagement data model."""

        # JSON encode test data
        test_data = jsonable_encoder(test_data)

        # Patch dataloader
        with MonkeyPatch.context() as patch:
            patch.setattr(dataloaders, "search_role_type", patch_loader(test_data))
            query = """
                query {
                    engagements {
                        org_unit_uuid
                        employee_uuid
                        engagement_type_uuid
                        job_function_uuid
                        leave_uuid
                        primary_uuid
                        is_primary
                        type
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
            """
            response = graphapi_test.post("/graphql", json={"query": query})

        data, errors = response.json().get("data"), response.json().get("errors")
        assert errors is None
        assert data is not None
        assert data["engagements"] == [
            {
                "org_unit_uuid": engagement["org_unit_uuid"],
                "employee_uuid": engagement["employee_uuid"],
                "engagement_type_uuid": engagement["engagement_type_uuid"],
                "job_function_uuid": engagement["job_function_uuid"],
                "leave_uuid": engagement["leave_uuid"],
                "primary_uuid": engagement["primary_uuid"],
                "is_primary": engagement["is_primary"],
                "type": engagement["type"],
                "fraction": engagement["fraction"],
                "validity": engagement["validity"],
                "extension_1": engagement["extension_1"],
                "extension_2": engagement["extension_2"],
                "extension_3": engagement["extension_3"],
                "extension_4": engagement["extension_4"],
                "extension_5": engagement["extension_5"],
                "extension_6": engagement["extension_6"],
                "extension_7": engagement["extension_7"],
                "extension_8": engagement["extension_8"],
                "extension_9": engagement["extension_9"],
                "extension_10": engagement["extension_10"],
            }
            for engagement in test_data
        ]

    @given(test_data=st.lists(st.builds(EngagementRead)), st_data=st.data())
    def test_query_by_uuid(self, test_data, st_data, graphapi_test, patch_loader):
        """Test that we can query engagements by UUID."""

        # Sample UUIDs
        uuids = [str(model.uuid) for model in test_data]
        test_uuids = st_data.draw(st.lists(st.sampled_from(uuids))) if uuids else []

        # JSON encode test data
        test_data = jsonable_encoder(test_data)

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
            response = graphapi_test.post(
                "/graphql", json={"query": query, "variables": {"uuids": test_uuids}}
            )

        data, errors = response.json().get("data"), response.json().get("errors")
        assert errors is None
        assert data is not None

        # Check UUID equivalence
        result_uuids = [assoc.get("uuid") for assoc in data["engagements"]]
        assert set(result_uuids) == set(test_uuids)
        assert len(result_uuids) == len(set(test_uuids))
