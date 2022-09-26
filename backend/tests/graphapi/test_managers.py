# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import pytest
from hypothesis import given
from pytest import MonkeyPatch

from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from mora.graphapi.shim import flatten_data
from mora.graphapi.versions.latest import dataloaders
from ramodels.mo.details import ManagerRead
from tests.conftest import GQLResponse


@given(test_data=graph_data_strat(ManagerRead))
def test_query_all(test_data, graphapi_post, patch_loader):
    """Test that we can query all attributes of the manager data model."""
    # Patch dataloader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "search_role_type", patch_loader(test_data))
        query = """
            query {
                managers {
                    uuid
                    objects {
                        uuid
                        user_key
                        employee_uuid
                        manager_level_uuid
                        manager_type_uuid
                        org_unit_uuid
                        responsibility_uuids
                        type
                        validity {from to}
                    }
                }
            }
        """
        response: GQLResponse = graphapi_post(query)

    assert response.errors is None
    assert response.data
    assert flatten_data(response.data["managers"]) == test_data


@given(test_input=graph_data_uuids_strat(ManagerRead))
def test_query_by_uuid(test_input, graphapi_post, patch_loader):
    """Test that we can query managers by UUID."""
    test_data, test_uuids = test_input

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
        response: GQLResponse = graphapi_post(query, {"uuids": test_uuids})

    assert response.errors is None
    assert response.data

    # Check UUID equivalence
    result_uuids = [manager.get("uuid") for manager in response.data["managers"]]
    assert set(result_uuids) == set(test_uuids)
    assert len(result_uuids) == len(set(test_uuids))


@pytest.mark.integration_test
@pytest.mark.usefixtures("sample_structures_no_reset")
@pytest.mark.parametrize(
    "filter_snippet,expected",
    [
        ("", 1),
        # Employee filters
        ('(employees: "53181ed2-f1de-4c4a-a8fd-ab358c2c454a")', 1),
        ('(employees: "6ee24785-ee9a-4502-81c2-7697009c9053")', 0),
        (
            """
            (employees: [
                "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                "6ee24785-ee9a-4502-81c2-7697009c9053"
            ])
        """,
            1,
        ),
        # Organisation Unit filter
        ('(org_units: "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e")', 1),
        ('(org_units: "2874e1dc-85e6-4269-823a-e1125484dfd3")', 0),
        (
            """
            (org_units: [
                "2874e1dc-85e6-4269-823a-e1125484dfd3",
                "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
            ])
        """,
            1,
        ),
        # Mixed filters
        (
            """
            (
                employees: "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                org_units: "2874e1dc-85e6-4269-823a-e1125484dfd3"
            )
        """,
            0,
        ),
        (
            """
            (
                employees: "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                org_units: "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
            )
        """,
            1,
        ),
    ],
)
async def test_manager_employees_filters(
    graphapi_post, filter_snippet, expected
) -> None:
    """Test filters on managers."""
    manager_query = f"""
        query Managers {{
            managers{filter_snippet} {{
                uuid
            }}
        }}
    """
    response: GQLResponse = graphapi_post(manager_query)
    assert response.errors is None
    assert len(response.data["managers"]) == expected
