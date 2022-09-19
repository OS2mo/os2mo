# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from hypothesis import given
from hypothesis import strategies as st
from mock import patch
from pytest import MonkeyPatch

from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from mora import mapping
from mora.graphapi.shim import flatten_data
from mora.graphapi.versions.latest import dataloaders
from mora.graphapi.versions.latest.version import LatestGraphQLSchema
from ramodels.mo import OrganisationUnitRead
from tests.conftest import GQLResponse


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


@given(
    st.uuids(),
    st.tuples(st.datetimes(), st.datetimes() | st.none()).filter(
        lambda dts: dts[0] <= dts[1] if dts[0] and dts[1] else True
    ),
)
async def test_update(given_uuid, given_validity_dts):
    given_validity_from, given_validity_to = given_validity_dts

    var_values = {
        mapping.UUID: str(given_uuid),
        mapping.FROM: given_validity_from.replace(
            hour=0, minute=0, second=0, microsecond=0
        ).isoformat(),
    }

    if given_validity_to:
        var_values["to"] = given_validity_to.date().isoformat()

    mutation_func = "org_unit_update"
    query = (
        "mutation($uuid: UUID!, $from: DateTime!, $to: DateTime, $orgUnitType: UUID) {"
        f"{mutation_func}(input: {{uuid: $uuid, from: $from, to: $to, "
        f"org_unit_type_uuid: $orgUnitType}})"
        "{ uuid }"
        "}"
    )

    with patch("mora.service.orgunit.lora.Scope.get") as mock_lora_get, patch(
        "mora.service.orgunit.lora.Scope.update"
    ) as mock_lora_update:
        # mock_lora_get.return_value = "Feraidoon yyyeeehhaaa"
        mock_lora_get.return_value = {
            "attributter": {
                "organisationenhedegenskaber": [
                    {
                        "brugervendtnoegle": "Viuf skole",
                        "enhedsnavn": "Viuf skole",
                        "virkning": {
                            "from": "1959-12-31 23:00:00+00",
                            "to": "infinity",
                            "from_included": True,
                            "to_included": False,
                        },
                    }
                ]
            },
            "tilstande": {
                "organisationenhedgyldighed": [
                    {
                        "virkning": {
                            "from": "1959-12-31 23:00:00+00",
                            "to": "infinity",
                            "from_included": True,
                            "to_included": False,
                        },
                        "gyldighed": "Aktiv",
                    }
                ]
            },
        }
        mock_lora_update.return_value = str(given_uuid)
        mock_lora_get.test_func = lambda a: print(a)

        response = await LatestGraphQLSchema.get().execute(
            query, variable_values=var_values
        )

        #        testings = "test"
        mock_lora_get.assert_called()
        mock_lora_update.assert_called()

        response_uuid = None
        if isinstance(response.data, dict):
            response_uuid = response.data.get(mutation_func, {}).get(mapping.UUID)

        assert response_uuid == str(given_uuid)


def thor_er_rigtig_sej():
    return "you know it"

def sexy_method():
    return "i know it"

def hammer_time():
    return "now?"
