# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import patch
from uuid import UUID

import pytest
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


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
def test_itsystem_create(graphapi_post) -> None:
    """Test that we can create new itsystems."""

    existing_itsystem_uuids = {
        UUID("0872fb72-926d-4c5c-a063-ff800b8ee697"),
        UUID("14466fb0-f9de-439c-a6c2-b3262c367da7"),
        UUID("59c135c9-2b15-41cc-97c8-b5dff7180beb"),
    }

    query = """
        query ReadITSystems {
            itsystems {
                uuid
                user_key
                name
            }
        }
    """
    response: GQLResponse = graphapi_post(query)
    assert response.errors is None
    assert response.data
    itsystem_map = {UUID(x["uuid"]): x for x in response.data["itsystems"]}
    assert itsystem_map.keys() == existing_itsystem_uuids

    mutation = """
        mutation CreateITSystem($input: ITSystemCreateInput!) {
            itsystem_create(input: $input) {
                uuid
            }
        }
    """
    response: GQLResponse = graphapi_post(
        mutation, {"input": {"user_key": "my_user_key", "name": "my_name"}}
    )
    assert response.errors is None
    assert response.data
    new_uuid = UUID(response.data["itsystem_create"]["uuid"])

    response: GQLResponse = graphapi_post(query)
    assert response.errors is None
    assert response.data
    itsystem_map = {UUID(x["uuid"]): x for x in response.data["itsystems"]}
    assert itsystem_map.keys() == existing_itsystem_uuids | {new_uuid}

    itsystem = itsystem_map[new_uuid]
    assert itsystem["name"] == "my_name"
    assert itsystem["user_key"] == "my_user_key"


@given(uuid=..., user_key=..., name=...)
def test_itsystem_create_mocked(
    uuid: UUID, user_key: str, name: str, graphapi_post, get_valid_organisations: UUID
) -> None:
    """Test that create_or_import_object is called as expected."""
    mutation = """
        mutation CreateITSystem($input: ITSystemCreateInput!) {
            itsystem_create(input: $input) {
                uuid
            }
        }
    """
    with patch("oio_rest.db.create_or_import_object") as mock:
        mock.return_value = uuid

        response: GQLResponse = graphapi_post(
            mutation, {"input": {"user_key": user_key, "name": name}}
        )
        assert response.errors is None
        assert response.data
        new_uuid = UUID(response.data["itsystem_create"]["uuid"])
        assert new_uuid == uuid

        mock.assert_called_with(
            "itsystem",
            "",
            {
                "states": {
                    "itsystemgyldighed": [
                        {
                            "gyldighed": "Aktiv",
                            "virkning": {"from": "-infinity", "to": "infinity"},
                        }
                    ]
                },
                "attributes": {
                    "itsystemegenskaber": [
                        {
                            "brugervendtnoegle": user_key,
                            "virkning": {"from": "-infinity", "to": "infinity"},
                            "itsystemnavn": name,
                        }
                    ]
                },
                "relations": {
                    "tilknyttedeorganisationer": [
                        {
                            "uuid": str(get_valid_organisations),
                            "virkning": {"from": "-infinity", "to": "infinity"},
                        }
                    ]
                },
            },
        )
