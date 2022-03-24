# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from fastapi.encoders import jsonable_encoder
from hypothesis import given
from pytest import MonkeyPatch
from ramodels.mo.details import AssociationRead

import mora.graphapi.dataloaders as dataloaders
from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from mora.graphapi.shim import flatten_data

# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------


class TestAssociationsQuery:
    """Class collecting associations query tests.

    Data loaders are mocked to return specific values, generated via
    Hypothesis.
    MonkeyPatch.context is used as a context manager to achieve this,
    because mocks are *not* reset between invocations of Hypothesis examples.
    """

    @given(test_data=graph_data_strat(AssociationRead))
    def test_query_all(self, test_data, graphapi_test, patch_loader):
        """Test that we can query all our associations."""
        # JSON encode test data
        test_data = jsonable_encoder(test_data)

        # Patch dataloader
        with MonkeyPatch.context() as patch:
            patch.setattr(dataloaders, "search_role_type", patch_loader(test_data))
            query = """
                query {
                    associations {
                        uuid
                        objects {
                            uuid
                            user_key
                            org_unit_uuid
                            employee_uuid
                            association_type_uuid
                            primary_uuid
                            substitute_uuid
                            job_function_uuid
                            it_user_uuid
                            dynamic_classes { uuid }
                            type
                            validity {from to}
                        }
                    }
                }
            """
            response = graphapi_test.post("/graphql", json={"query": query})

        data, errors = response.json().get("data"), response.json().get("errors")
        assert errors is None
        assert data is not None
        assert flatten_data(data["associations"]) == test_data

    @given(test_input=graph_data_uuids_strat(AssociationRead))
    def test_query_by_uuid(self, test_input, graphapi_test, patch_loader):
        """Test that we can query associations by UUID."""
        # Sample UUIDs
        test_data, test_uuids = test_input

        # Patch dataloader
        with MonkeyPatch.context() as patch:
            patch.setattr(dataloaders, "get_role_type_by_uuid", patch_loader(test_data))
            query = """
                    query TestQuery($uuids: [UUID!]) {
                        associations(uuids: $uuids) {
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
        result_uuids = [assoc.get("uuid") for assoc in data["associations"]]
        assert set(result_uuids) == set(test_uuids)
        assert len(result_uuids) == len(set(test_uuids))
