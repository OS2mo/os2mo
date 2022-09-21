# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date
from uuid import UUID
from uuid import uuid4

import pytest
from pytest import MonkeyPatch

from mora.graphapi.shim import flatten_data
from mora.graphapi.versions.latest import dataloaders
from ramodels.mo import OrganisationUnitRead
from ramodels.mo import Validity
from tests.conftest import GQLResponse


@pytest.fixture
def parent_uuid() -> UUID:
    return uuid4()


@pytest.fixture
def get_response(parent_uuid, graphapi_post, patch_loader):
    def _get_response(url: str) -> GQLResponse:
        parent = OrganisationUnitRead(
            uuid=parent_uuid,
            name="parent",
            validity=Validity(from_date=date(2007, 8, 9), to_date=date(2026, 7, 8)),
            # root org unit(s) have the org singleton as parent, which won't exist as an
            # org unit.
            parent_uuid=uuid4(),
        )
        child = OrganisationUnitRead(
            name="child",
            validity=Validity(from_date=date(2011, 2, 3), to_date=date(2022, 3, 4)),
            parent_uuid=parent.uuid,
        )
        orphan = OrganisationUnitRead(
            name="orphan",
            validity=Validity(from_date=date(2011, 2, 3), to_date=date(2022, 3, 4)),
            # parent_uuid should never be none unless the database is fucked
            parent_uuid=None,
        )
        test_data = [parent, child, orphan]

        with MonkeyPatch.context() as patch:
            patch.setattr(dataloaders, "search_role_type", patch_loader(test_data))
            patch.setattr(dataloaders, "get_role_type_by_uuid", patch_loader([parent]))
            query = """
                query OrgUnitParentsQuery {
                  org_units {
                    objects {
                      parent {
                        uuid
                      }
                    }
                  }
                }
            """
            response = graphapi_post(query, url=url)
        return response

    return _get_response


def test_v1_shim_org_unit_parent(parent_uuid, get_response):
    """Test that the v1 API returns org unit parents as lists."""
    response = get_response("/graphql/v1")
    parents = flatten_data(response.data["org_units"])
    assert parents == [
        {"parent": []},  # parent
        {"parent": [{"uuid": str(parent_uuid)}]},  # child
        {"parent": None},  # orphan
    ]


def test_v2_shim_org_unit_parent(parent_uuid, get_response):
    """Test that the v2 API returns org unit parents directly."""
    response = get_response("/graphql/v2")
    parents = flatten_data(response.data["org_units"])
    assert parents == [
        {"parent": None},  # parent
        {"parent": {"uuid": str(parent_uuid)}},  # child
        {"parent": None},  # orphan
    ]
