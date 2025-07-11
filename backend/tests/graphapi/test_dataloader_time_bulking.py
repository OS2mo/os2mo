# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from unittest.mock import ANY
from unittest.mock import MagicMock
from unittest.mock import call
from uuid import UUID

import pytest
from mora.graphapi.versions.latest.dataloaders import load_mo
from mora.graphapi.versions.latest.graphql_utils import LoadKey
from mora.graphapi.versions.latest.schema import ClassRead
from mora.graphapi.versions.latest.schema import OrganisationUnitRead
from more_itertools import one

from tests.conftest import GraphAPIPost


class AnyOrder(list):
    def __eq__(self, other):
        if isinstance(other, list):
            if len(self) != len(other):
                return False
            s_self = sorted(self)
            s_other = sorted(other)
            return s_self == s_other
        raise NotImplementedError("Only support lists")


@pytest.fixture
def create_org_unit(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        mutate_query = """
            mutation CreateOrgUnit($input: OrganisationUnitCreateInput!) {
                org_unit_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(query=mutate_query, variables={"input": input})
        assert response.errors is None
        assert response.data
        return UUID(response.data["org_unit_create"]["uuid"])

    return inner


@pytest.fixture
async def read_org_unit_types(
    graphapi_post: GraphAPIPost,
) -> Callable[[], dict[UUID, UUID]]:
    def inner() -> dict[UUID, UUID]:
        org_unit_type_query = """
            query ReadOrgUnitTypes {
                org_units {
                    objects {
                        current {
                            uuid
                            unit_type {
                                uuid
                            }
                        }
                    }
                }
            }
        """
        response = graphapi_post(org_unit_type_query)
        assert response.errors is None
        assert response.data
        org_unit_type_map = {
            UUID(org_unit["current"]["uuid"]): UUID(
                org_unit["current"]["unit_type"]["uuid"]
            )
            for org_unit in response.data["org_units"]["objects"]
        }
        return org_unit_type_map

    return inner


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.xfail(reason="DataLoader bulking is underutilised")
def test_dataloader_time_bulking(
    monkeypatch: pytest.MonkeyPatch,
    org_unit_type_facet: UUID,
    create_class: Callable[[dict[str, Any]], UUID],
    create_org_unit: Callable[[dict[str, Any]], UUID],
    read_org_unit_types: Callable[[], dict[UUID, UUID]],
) -> None:
    # Construct two org_unit_type classes
    department_class = create_class(
        {
            "user_key": "department",
            "name": "Department",
            "facet_uuid": str(org_unit_type_facet),
            "validity": {"from": "1970-01-01"},
        }
    )
    external_class = create_class(
        {
            "user_key": "external",
            "name": "External Company",
            "facet_uuid": str(org_unit_type_facet),
            "validity": {"from": "1970-01-01"},
        }
    )

    # Construct two org-units one per org_unit_type
    dph = create_org_unit(
        {
            "name": "Department of Hope",
            "user_key": "dph",
            "parent": None,
            "validity": {"from": "1970-01-01T00:00:00Z"},
            "org_unit_type": str(department_class),
        }
    )
    maps = create_org_unit(
        {
            "name": "Magenta ApS",
            "user_key": "maps",
            "parent": None,
            "validity": {"from": "1970-01-01T00:00:00Z"},
            "org_unit_type": str(external_class),
        }
    )

    # Read out org-units with their org_unit_types, verify they read as expected
    org_unit_type_map = read_org_unit_types()
    assert org_unit_type_map == {dph: department_class, maps: external_class}

    # Man-in-the-middle the load_mo function with a transparent spy mock
    # The spy mocks behave exactly like underlying function (i.e. the load_mo function),
    # only it allows us to assert which calls have been made through the mock.
    load_mo_spy = MagicMock(wraps=load_mo)
    monkeypatch.setattr(
        "mora.graphapi.versions.latest.dataloaders.load_mo", load_mo_spy
    )

    # Verify that our mocks did not change the functionality of the code
    org_unit_type_map_mocked = read_org_unit_types()
    assert org_unit_type_map_mocked == org_unit_type_map

    # Check that the calls through the mock are as expected
    assert load_mo_spy.mock_calls == [
        call(
            AnyOrder(
                [
                    LoadKey(uuid=dph, start=ANY, end=ANY),
                    LoadKey(uuid=maps, start=ANY, end=ANY),
                ]
            ),
            model=OrganisationUnitRead,
        ),
        call(
            AnyOrder(
                [
                    LoadKey(uuid=department_class, start=ANY, end=ANY),
                    LoadKey(uuid=external_class, start=ANY, end=ANY),
                ]
            ),
            model=ClassRead,
        ),
    ]
    # Check that the classes have same start and end time
    # (otherwise they cannot be bulked)
    org_call, class_call = load_mo_spy.mock_calls
    lk1, lk2 = one(class_call.args)
    assert lk1.start == lk2.start
    assert lk1.end == lk2.end
