# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from hypothesis import given
from pydantic import parse_obj_as
from pytest import MonkeyPatch

import mora.lora as lora
from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from mora.graphapi.versions.latest import dataloaders
from ramodels.mo.details import ITSystemRead
from tests.conftest import GQLResponse


@given(test_data=graph_data_strat(ITSystemRead))
def test_query_all(test_data, graphapi_post, patch_loader):
    """Test that we can query all attributes of the ITSystem data model."""
    # Patch dataloader
    with MonkeyPatch.context() as patch:
        # Our IT system dataloaders are ~* special *~
        # We need to intercept the connector too
        patch.setattr(lora.Scope, "get_all", patch_loader({}))
        patch.setattr(
            dataloaders,
            "lora_itsystem_to_mo_itsystem",
            lambda *args, **kwargs: parse_obj_as(list[ITSystemRead], test_data),
        )
        query = """
            query {
                itsystems {
                    uuid
                    name
                    system_type
                    type
                    user_key
                    uuid
                }
            }
        """
        response: GQLResponse = graphapi_post(query)

    assert response.errors is None
    assert response.data
    assert response.data["itsystems"] == test_data


@given(test_input=graph_data_uuids_strat(ITSystemRead))
def test_query_by_uuid(test_input, graphapi_post, patch_loader):
    """Test that we can query ITSystems by UUID."""
    test_data, test_uuids = test_input

    # Patch dataloader
    with MonkeyPatch.context() as patch:
        # Our facet dataloaders are ~* special *~
        # We need to intercept the connector too
        patch.setattr(lora.Scope, "get_all_by_uuid", patch_loader({}))
        patch.setattr(
            dataloaders,
            "lora_itsystem_to_mo_itsystem",
            lambda *args, **kwargs: parse_obj_as(list[ITSystemRead], test_data),
        )
        query = """
                query TestQuery($uuids: [UUID!]) {
                    itsystems(uuids: $uuids) {
                        uuid
                    }
                }
            """
        response: GQLResponse = graphapi_post(query, {"uuids": test_uuids})

    assert response.errors is None
    assert response.data

    # Check UUID equivalence
    result_uuids = [itsys.get("uuid") for itsys in response.data["itsystems"]]
    assert set(result_uuids) == set(test_uuids)
    assert len(result_uuids) == len(set(test_uuids))
