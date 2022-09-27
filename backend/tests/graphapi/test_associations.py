# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import pytest
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
        # Association type ilter
        ('(association_types: "62ec821f-4179-4758-bfdf-134529d186e9")', 0),
        ('(association_type_user_keys: "medl")', 0),
        ('(association_types: "8eea787c-c2c7-46ca-bd84-2dd50f47801e")', 0),
        ('(association_type_user_keys: "projektleder")', 0),
        ('(association_types: "45751985-321f-4d4f-ae16-847f0a633360")', 0),
        ('(association_type_user_keys: "teammedarbejder")', 0),
        (
            """
            (association_types: [
                "62ec821f-4179-4758-bfdf-134529d186e9",
                "8eea787c-c2c7-46ca-bd84-2dd50f47801e"
            ])
        """,
            0,
        ),
        (
            """
            (
                association_types: "62ec821f-4179-4758-bfdf-134529d186e9",
                association_type_user_keys: "projektleder"
            )
        """,
            0,
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
async def test_association_filters(graphapi_post, filter_snippet, expected) -> None:
    """Test filters on associations."""
    association_query = f"""
        query Managers {{
            associations{filter_snippet} {{
                uuid
            }}
        }}
    """
    response: GQLResponse = graphapi_post(association_query)
    assert response.errors is None
    assert len(response.data["associations"]) == expected
