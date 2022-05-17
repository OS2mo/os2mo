# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from hypothesis import given
from pydantic import parse_obj_as
from pytest import MonkeyPatch
from ramodels.mo import FacetRead

import mora.graphapi.dataloaders as dataloaders
import mora.lora as lora
from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from tests.conftest import GQLResponse

# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------


class TestFacetsQuery:
    """Class collecting facets query tests.

    Data loaders are mocked to return specific values, generated via
    Hypothesis.
    MonkeyPatch.context is used as a context manager to achieve this,
    because mocks are *not* reset between invocations of Hypothesis examples.
    """

    @given(test_data=graph_data_strat(FacetRead))
    def test_query_all(self, test_data, graphapi_post, patch_loader):
        """Test that we can query all attributes of the facets data model."""
        # Patch dataloader
        with MonkeyPatch.context() as patch:
            # Our facet dataloaders are ~* special *~
            # We need to intercept the connector too
            patch.setattr(lora.Scope, "get_all", patch_loader({}))
            patch.setattr(
                dataloaders,
                "lora_facets_to_mo_facets",
                lambda *args, **kwargs: parse_obj_as(list[FacetRead], test_data),
            )
            query = """
                query {
                    facets {
                        uuid
                        user_key
                        description
                        parent_uuid
                        org_uuid
                        published
                        type
                    }
                }
            """
            response: GQLResponse = graphapi_post(query)

        assert response.errors is None
        assert response.data
        assert response.data["facets"] == test_data

    @given(test_input=graph_data_uuids_strat(FacetRead))
    def test_query_by_uuid(self, test_input, graphapi_post, patch_loader):
        """Test that we can query facets by UUID."""
        test_data, test_uuids = test_input

        # Patch dataloader
        with MonkeyPatch.context() as patch:
            # Our facet dataloaders are ~* special *~
            # We need to intercept the connector too
            patch.setattr(lora.Scope, "get_all_by_uuid", patch_loader({}))
            patch.setattr(
                dataloaders,
                "lora_facets_to_mo_facets",
                lambda *args, **kwargs: parse_obj_as(list[FacetRead], test_data),
            )
            query = """
                    query TestQuery($uuids: [UUID!]) {
                        facets(uuids: $uuids) {
                            uuid
                        }
                    }
                """
            response: GQLResponse = graphapi_post(query, {"uuids": test_uuids})

        assert response.errors is None
        assert response.data

        # Check UUID equivalence
        result_uuids = [facet.get("uuid") for facet in response.data["facets"]]
        assert set(result_uuids) == set(test_uuids)
        assert len(result_uuids) == len(set(test_uuids))
