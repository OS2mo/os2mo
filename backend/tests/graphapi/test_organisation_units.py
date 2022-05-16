#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from hypothesis import given
from pytest import MonkeyPatch
from ramodels.mo import OrganisationUnitRead

import mora.graphapi.dataloaders as dataloaders
from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from mora.graphapi.shim import flatten_data


# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------


class TestOrganisationUnitsQuery:
    """Class collecting organisation unit query tests.

    Data loaders are mocked to return specific values, generated via
    Hypothesis.
    MonkeyPatch.context is used as a context manager to achieve this,
    because mocks are *not* reset between invocations of Hypothesis examples.
    """

    @given(test_data=graph_data_strat(OrganisationUnitRead))
    def test_query_all(self, test_data, graphapi_test, patch_loader):
        """Test that we can query all our organisation units."""
        # Patch dataloader
        with MonkeyPatch.context() as patch:
            patch.setattr(dataloaders, "search_role_type", patch_loader(test_data))
            query = """
                query {
                    org_units {
                        uuid
                        objects {
                            uuid
                            user_key
                            name
                            type
                            validity {from to}
                            parent_uuid
                            unit_type_uuid
                            org_unit_hierarchy
                            org_unit_level_uuid
                            time_planning_uuid
                        }

                    }
                }
            """
            with graphapi_test as client:
                response = client.post("/graphql", json={"query": query})

        data, errors = response.json().get("data"), response.json().get("errors")
        assert errors is None
        assert data is not None
        assert flatten_data(data["org_units"]) == test_data

    @given(test_input=graph_data_uuids_strat(OrganisationUnitRead))
    def test_query_by_uuid(self, test_input, graphapi_test, patch_loader):
        """Test that we can query organisation units by UUID."""
        test_data, test_uuids = test_input

        # Patch dataloader
        with MonkeyPatch.context() as patch:
            patch.setattr(dataloaders, "get_role_type_by_uuid", patch_loader(test_data))
            query = """
                    query TestQuery($uuids: [UUID!]) {
                        org_units(uuids: $uuids) {
                            uuid
                        }
                    }
                """
            with graphapi_test as client:
                response = client.post(
                    "/graphql",
                    json={"query": query, "variables": {"uuids": test_uuids}},
                )

        data, errors = response.json().get("data"), response.json().get("errors")
        assert errors is None
        assert data is not None

        # Check UUID equivalence
        result_uuids = [ou.get("uuid") for ou in data["org_units"]]
        assert set(result_uuids) == set(test_uuids)
        assert len(result_uuids) == len(set(test_uuids))
