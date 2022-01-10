# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from fastapi.encoders import jsonable_encoder
from hypothesis import given
from hypothesis import strategies as st
from pytest import MonkeyPatch
from ramodels.mo.details import ManagerRead

import mora.graphapi.dataloaders as dataloaders
from mora.graphapi.main import get_schema

# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------

SCHEMA = str(get_schema())


class TestManagersQuery:
    """Class collecting managers query tests.

    Data loaders are mocked to return specific values, generated via
    Hypothesis.
    MonkeyPatch.context is used as a context manager to achieve this,
    because mocks are *not* reset between invocations of Hypothesis examples.
    """

    @given(test_data=st.lists(st.builds(ManagerRead)))
    def test_query_all(self, test_data, graphapi_test, patch_loader):
        """Test that we can query all attributes of the manager data model."""

        # JSON encode test data
        test_data = jsonable_encoder(test_data)

        # Patch dataloader
        with MonkeyPatch.context() as patch:
            patch.setattr(dataloaders, "search_role_type", patch_loader(test_data))
            query = """
                query {
                    managers {
                        employee_uuid
                        manager_level_uuid
                        manager_type_uuid
                        org_unit_uuid
                        responsibility_uuids
                        type
                        validity {from to}
                    }
                }
            """
            response = graphapi_test.post("/graphql", json={"query": query})

        data, errors = response.json().get("data"), response.json().get("errors")
        assert errors is None
        assert data is not None
        assert data["managers"] == [
            {
                "employee_uuid": manager["employee_uuid"],
                "manager_level_uuid": manager["manager_level_uuid"],
                "manager_type_uuid": manager["manager_type_uuid"],
                "org_unit_uuid": manager["org_unit_uuid"],
                "responsibility_uuids": manager["responsibility_uuids"],
                "type": manager["type"],
                "validity": manager["validity"],
            }
            for manager in test_data
        ]

    @given(test_data=st.lists(st.builds(ManagerRead)), st_data=st.data())
    def test_query_by_uuid(self, test_data, st_data, graphapi_test, patch_loader):
        """Test that we can query managers by UUID."""

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
                        managers(uuids: $uuids) {
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
        result_uuids = [assoc.get("uuid") for assoc in data["managers"]]
        assert set(result_uuids) == set(test_uuids)
        assert len(result_uuids) == len(set(test_uuids))
