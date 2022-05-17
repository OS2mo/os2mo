# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from hypothesis import given
from pydantic import parse_obj_as
from pytest import MonkeyPatch
from ramodels.mo import ClassRead

import mora.graphapi.dataloaders as dataloaders
import mora.lora as lora
from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from tests.conftest import GQLResponse

# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------


class TestClassesQuery:
    """Class collecting classes query tests.

    Data loaders are mocked to return specific values, generated via
    Hypothesis.
    MonkeyPatch.context is used as a context manager to achieve this,
    because mocks are *not* reset between invocations of Hypothesis examples.
    """

    @given(test_data=graph_data_strat(ClassRead))
    def test_query_all(self, test_data, graphapi_post, graphapi_test, patch_loader):
        """Test that we can query all attributes of the classes data model."""
        # patch get_classes to return list(ClassRead)
        with MonkeyPatch.context() as patch:
            # Our class dataloaders are ~* special *~
            # We need to intercept the connector too
            patch.setattr(lora.Scope, "get_all", patch_loader({}))
            patch.setattr(
                dataloaders,
                "lora_classes_to_mo_classes",
                lambda *args, **kwargs: parse_obj_as(list[ClassRead], test_data),
            )
            query = """
                query {
                    classes {
                        uuid
                        user_key
                        facet_uuid
                        example
                        owner
                        org_uuid
                        name
                        parent_uuid
                        published
                        scope
                        type
                    }
                }
            """
            response: GQLResponse = graphapi_post(query=query)

        assert response.errors is None
        assert response.data
        assert response.data["classes"] == test_data

    @given(test_input=graph_data_uuids_strat(ClassRead))
    def test_query_by_uuid(self, test_input, graphapi_post, patch_loader):
        """Test that we can query classes by UUID."""
        test_data, test_uuids = test_input
        # Patch dataloader
        with MonkeyPatch.context() as patch:
            # Our class dataloaders are ~* special *~
            # We need to intercept the connector too
            patch.setattr(lora.Scope, "get_all_by_uuid", patch_loader({}))
            patch.setattr(
                dataloaders,
                "lora_classes_to_mo_classes",
                lambda *args, **kwargs: parse_obj_as(list[ClassRead], test_data),
            )
            query = """
                    query TestQuery($uuids: [UUID!]) {
                        classes(uuids: $uuids) {
                            uuid
                        }
                    }
                """
            response: GQLResponse = graphapi_post(query, {"uuids": test_uuids})

        assert response.errors is None
        assert response.data

        # Check UUID equivalence
        result_uuids = [cla.get("uuid") for cla in response.data["classes"]]
        assert set(result_uuids) == set(test_uuids)
        assert len(result_uuids) == len(set(test_uuids))
