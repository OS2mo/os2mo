# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import datetime

from unittest.mock import AsyncMock
from unittest.mock import patch
from uuid import uuid4

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pytest import MonkeyPatch

from mora.graphapi.versions.latest.types import OrganisationUnitType
from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from mora import mapping
from mora.graphapi.shim import flatten_data
from mora.graphapi.versions.latest import dataloaders
from mora.graphapi.versions.latest.version import LatestGraphQLSchema
from ramodels.mo import OrganisationUnitRead
from tests.conftest import GQLResponse

from mora.graphapi.versions.latest.models import OrganisationUnitUpdate
from fastapi.encoders import jsonable_encoder
from mora.graphapi.shim import execute_graphql
from operator import itemgetter
from uuid import UUID
from more_itertools import one
from ramodels.mo import Validity as RAValidity


@given(test_data=graph_data_strat(OrganisationUnitRead))
def test_query_all(test_data, graphapi_post, patch_loader):
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
        response = graphapi_post(query)

    assert response.errors is None
    assert response.data
    assert flatten_data(response.data["org_units"]) == test_data


@given(test_input=graph_data_uuids_strat(OrganisationUnitRead))
def test_query_by_uuid(test_input, graphapi_post, patch_loader):
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
        response: GQLResponse = graphapi_post(query, {"uuids": test_uuids})

    assert response.errors is None
    assert response.data

    # Check UUID equivalence
    result_uuids = [ou.get("uuid") for ou in response.data["org_units"]]
    assert set(result_uuids) == set(test_uuids)
    assert len(result_uuids) == len(set(test_uuids))


#
# @given(
#     st.uuids(),
#     st.tuples(st.datetimes(), st.datetimes() | st.none()).filter(
#         lambda dts: dts[0] <= dts[1] if dts[0] and dts[1] else True
#     ),
# )
# async def test_update(given_uuid, given_validity_dts):
#     given_validity_from, given_validity_to = given_validity_dts
#
#     var_values = {
#         mapping.UUID: str(given_uuid),
#         mapping.FROM: given_validity_from.replace(
#             hour=0, minute=0, second=0, microsecond=0
#         ).isoformat(),
#     }
#
#     if given_validity_to:
#         var_values["to"] = given_validity_to.date().isoformat()
#
#     mutation_func = "org_unit_update"
#     query = (
#         "mutation($uuid: UUID!, $from: DateTime!, $to: DateTime, $orgUnitType: UUID) {"
#         f"{mutation_func}(input: {{uuid: $uuid, from: $from, to: $to, "
#         f"org_unit_type_uuid: $orgUnitType}})"
#         "{ uuid }"
#         "}"
#     )
#
#     with patch("mora.service.orgunit.lora.Scope.get") as mock_lora_get, patch(
#         "mora.service.orgunit.lora.Scope.update"
#     ) as mock_lora_update:
#         # mock_lora_get.return_value = "Feraidoon yyyeeehhaaa"
#         mock_lora_get.return_value = {
#             "attributter": {
#                 "organisationenhedegenskaber": [
#                     {
#                         "brugervendtnoegle": "Viuf skole",
#                         "enhedsnavn": "Viuf skole",
#                         "virkning": {
#                             "from": "1959-12-31 23:00:00+00",
#                             "to": "infinity",
#                             "from_included": True,
#                             "to_included": False,
#                         },
#                     }
#                 ]
#             },
#             "tilstande": {
#                 "organisationenhedgyldighed": [
#                     {
#                         "virkning": {
#                             "from": "1959-12-31 23:00:00+00",
#                             "to": "infinity",
#                             "from_included": True,
#                             "to_included": False,
#                         },
#                         "gyldighed": "Aktiv",
#                     }
#                 ]
#             },
#         }
#         mock_lora_update.return_value = str(given_uuid)
#         mock_lora_get.test_func = lambda a: print(a)
#
#         response = await LatestGraphQLSchema.get().execute(
#             query, variable_values=var_values
#         )
#
#         #        testings = "test"
#         mock_lora_get.assert_called()
#         mock_lora_update.assert_called()
#
#         response_uuid = None
#         if isinstance(response.data, dict):
#             response_uuid = response.data.get(mutation_func, {}).get(mapping.UUID)
#
#         assert response_uuid == str(given_uuid)
#
#
# now_beginning = datetime.datetime.now().replace(
#     hour=0, minute=0, second=0, microsecond=0
# )
#
#
# @pytest.mark.parametrize("names, cprs, org_uuids, expected_result", [
#     ("Laura", "0103882148", "3b866d97-0b1f-48e0-8078-686d96f430b3", True)
# ])

# @given(
#     given_names=st.text(), given_type_uuids=st.uuids(), given_level_uuids=st.uuids(),
#     given_hierarchy_uuids=st.uuids(), given_parent_uuids=st.uuids(),
#     given_time_plannings=st.uuids(), given_locations=st.uuids()
# )
@pytest.mark.parametrize(
    "given_from_dates, given_to_dates ,given_names, given_type_uuids, "
    "given_level_uuids, given_hierarchy_uuids, given_parent_uuids, "
    "given_time_plannings, given_locations",
    [
        (
            "1959-12-31 23:00:00+00",  # 0001-01-01 00:00:00+00:00
            "1969-12-31 23:00:00+00",  # 9999-12-31 23:59:59.999999+00:00
            "Jannick",
            "08eaf849-e9f9-53e0-b6b9-3cd45763ecbb",
            "08eaf849-e9f9-53e0-b6b9-3cd45763ecbb",
            "08eaf849-e9f9-53e0-b6b9-3cd45763ecbb",
            "08eaf849-e9f9-53e0-b6b9-3cd45763ecbb",
            "08eaf849-e9f9-53e0-b6b9-3cd45763ecbb",
            "08eaf849-e9f9-53e0-b6b9-3cd45763ecbb",
        )
    ],
)
async def test_mutator_for_updating_org_unit(
    given_from_dates,
    given_to_dates,
    given_names,
    given_type_uuids,
    given_level_uuids,
    given_hierarchy_uuids,
    given_parent_uuids,
    given_time_plannings,
    given_locations,
):
    with patch(
        "mora.graphapi.versions.latest.org_unit.OrgUnitRequestHandler.construct"
    ) as mock_org_unit_request_handler:
        mock_new_uuids = str(uuid4())
        mock_submit = AsyncMock(return_value=mock_new_uuids)
        mock_org_unit_request_handler.return_value = AsyncMock(submit=mock_submit)

        mutation_func = "org_unit_update"
        query = (
            "mutation($from: DateTime, $to: DateTime, $name: String, "
            "$org_unit_type_uuid: UUID, $org_unit_level_uuid: UUID, "
            "$org_unit_hierarchy_uuid: UUID, $parent_uuid: UUID, $time_planning: UUID, "
            "$location: UUID) {"
            f"{mutation_func} (input: {{from: $from, to: $to, "
            "name: $name, org_unit_type_uuid: $org_unit_type_uuid, "
            "org_unit_level_uuid: $org_unit_level_uuid,"
            "org_unit_hierarchy_uuid: $org_unit_hierarchy_uuid, parent_uuid: "
            "$parent_uuid, time_planning: $time_planning, location: $location})"
            "{ uuid }"
            "}"
        )

        var_values = {}
        if given_from_dates:
            var_values["from"] = {mapping.FROM: given_from_dates}

        if given_to_dates:
            var_values["to"] = {mapping.TO: given_to_dates}

        if given_names:
            var_values["name"] = given_names

        if given_type_uuids:
            var_values["org_unit_type_uuid"] = {mapping.UUID: given_type_uuids}

        if given_level_uuids:
            var_values["org_unit_level_uuid"] = {mapping.UUID: given_level_uuids}

        if given_hierarchy_uuids:
            var_values["org_unit_hierarchy_uuid"] = {
                mapping.UUID: given_hierarchy_uuids
            }

        if given_parent_uuids:
            var_values["parent_uuid"] = {mapping.UUID: given_parent_uuids}

        if given_time_plannings:
            var_values["time_planning"] = {mapping.UUID: given_time_plannings}

        if given_locations:
            var_values["location"] = {mapping.UUID: given_locations}

        response = await LatestGraphQLSchema.get().execute(
            query, variable_values=var_values
        )

    assert var_values["name"] == "Jannick"
    # assert response.data.get(mutation_func, {}).get("uuid", None) == mock_new_uuids


@given(test_data=...)
@patch("mora.graphapi.versions.latest.mutators.create_org_unit", new_callable=AsyncMock)
async def test_create_org_unit(
    update_org_unit: AsyncMock, test_data: OrganisationUnitUpdate
) -> None:
    """Test that pydantic jsons are passed through to update_org_unit."""

    # mutate_query = """
    #     mutation CreateOrgUnit($input: OrganisationUnitUpdateInput!) {
    #         update_org_unit(input: $input) {
    #             uuid
    #         }
    #     }
    # """

    mutation_func = "org_unit_update"
    query = (
        "mutation($from: DateTime, $to: DateTime, $name: String, "
        "$org_unit_type_uuid: UUID, $org_unit_level_uuid: UUID, "
        "$org_unit_hierarchy_uuid: UUID, $parent_uuid: UUID, $time_planning: UUID, "
        "$location: UUID) {"
        f"{mutation_func} (input: {{from: $from, to: $to, "
        "name: $name, org_unit_type_uuid: $org_unit_type_uuid, "
        "org_unit_level_uuid: $org_unit_level_uuid,"
        "org_unit_hierarchy_uuid: $org_unit_hierarchy_uuid, parent_uuid: "
        "$parent_uuid, time_planning: $time_planning, location: $location})"
        "{ uuid }"
        "}"
    )

    created_uuid = uuid4()
    update_org_unit.return_value = OrganisationUnitType(uuid=created_uuid)

    payload = jsonable_encoder(test_data)
    response = await execute_graphql(
        query=query, variable_values={"input": payload}
    )
    assert response.errors is None
    assert response.data == {"update_org_unit": {"uuid": str(created_uuid)}}

    update_org_unit.assert_called_with(test_data)
