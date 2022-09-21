# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from fastapi.encoders import jsonable_encoder
from hypothesis import given
from pytest import MonkeyPatch

from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from mora.graphapi.shim import flatten_data
from mora.graphapi.versions.latest import dataloaders
from ramodels.mo.details import AssociationRead
from tests.conftest import GQLResponse


@given(test_data=graph_data_strat(AssociationRead))
def test_query_all(test_data, graphapi_post, patch_loader):
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
                        dynamic_class_uuid
                        type
                        validity {from to}
                    }
                }
            }
        """
        response = graphapi_post(query)

    assert response.errors is None
    assert response.data
    assert flatten_data(response.data["associations"]) == test_data


@given(test_input=graph_data_uuids_strat(AssociationRead))
def test_query_by_uuid(test_input, graphapi_post, patch_loader):
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
        response: GQLResponse = graphapi_post(query, {"uuids": test_uuids})

    assert response.errors is None
    assert response.data

    # Check UUID equivalence
    result_uuids = [assoc.get("uuid") for assoc in response.data["associations"]]
    assert set(result_uuids) == set(test_uuids)
    assert len(result_uuids) == len(set(test_uuids))
