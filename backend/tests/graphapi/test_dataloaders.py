# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests of dataloaders used in the GraphQL implementation."""
import uuid
from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest
from hypothesis import given
from more_itertools import one
from pytest import MonkeyPatch

from .strategies import data_strat
from .strategies import data_with_uuids_strat
from mora.graphapi.versions.latest import dataloaders
from mora.graphapi.versions.latest.dataloaders import get_classes
from mora.graphapi.versions.latest.schema import AddressRead
from mora.graphapi.versions.latest.schema import AssociationRead
from mora.graphapi.versions.latest.schema import EmployeeRead
from mora.graphapi.versions.latest.schema import EngagementRead
from mora.graphapi.versions.latest.schema import ITUserRead
from mora.graphapi.versions.latest.schema import KLERead
from mora.graphapi.versions.latest.schema import LeaveRead
from mora.graphapi.versions.latest.schema import ManagerRead
from mora.graphapi.versions.latest.schema import OrganisationUnitRead
from mora.graphapi.versions.latest.schema import RelatedUnitRead
from mora.graphapi.versions.latest.schema import RoleRead

pytestmark = pytest.mark.asyncio

models = [
    AddressRead,
    AssociationRead,
    EmployeeRead,
    EngagementRead,
    ITUserRead,
    KLERead,
    LeaveRead,
    ManagerRead,
    OrganisationUnitRead,
    RelatedUnitRead,
    RoleRead,
]


@pytest.mark.skip(reason="We need a LoRa dataset for these to make sense")
class TestDataloaders:
    """Class collecting dataloader tests."""

    @given(test_data=data_strat(models))
    async def test_get(self, test_data, patch_loader):
        """Test get of all models."""
        # Sample data
        model, data = test_data

        # Patch getter
        with MonkeyPatch.context() as patch:
            patch.setattr(dataloaders, "search_role_type", patch_loader(data))
            result = await dataloaders.get_mo(model)

        # The dataloader does not filter data, and as such we expect equality.
        assert result == data

    @given(test_data=data_with_uuids_strat(models))
    async def test_load(self, test_data, patch_loader):
        """Test load of models."""
        # Sample data & UUIDs
        model, data, uuids, _ = test_data

        # Patch loader
        with MonkeyPatch.context() as patch:
            patch.setattr(dataloaders, "get_role_type_by_uuid", patch_loader(data))
            result = await dataloaders.load_mo(uuids, model)

        # We expect as many results as there are UUIDs passed to the function.
        # Additionally, the result must be an improper subset of the test data.
        assert len(result) == len(uuids)
        data_map = {model.uuid: model for model in data}
        result_map = {model.uuid: model for model in result}
        assert result_map.items() <= data_map.items()

    @given(test_data=data_with_uuids_strat(models))
    async def test_load_nonexistent(self, test_data, patch_loader):
        """Test load of UUIDs that do not exist in data, including the empty list."""
        # Sample data & UUIDs
        model, data, _, other_uuids = test_data

        # Patch loader
        with MonkeyPatch.context() as patch:
            patch.setattr(dataloaders, "get_role_type_by_uuid", patch_loader(data))
            result = await dataloaders.load_mo(other_uuids, model)

        # Again, we expect as many results as there are UUIDs passed to the function.
        # Additionally, results are either {None} or the empty set.
        assert len(result) == len(other_uuids)
        if other_uuids:
            assert set(result) == {None}
        else:
            assert set(result) == set()


@patch("mora.lora.Scope.get_all", new_callable=AsyncMock)
async def test_get_classes_with_effects(mock_get_all):
    facet_assoc_type_uuid = uuid.UUID("9cbad2e8-8f3d-4549-b189-d10f745b912d")
    not_published_name = "-"
    not_published_state = "ikkePubliceret"

    mock_get_all.return_value = [
        (
            "17e4d114-fdb7-4ff9-ae98-37d47589f557",
            {
                "fratidspunkt": {
                    "tidsstempeldatotid": "2023-02-21T16:45:16.522349+01:00",
                    "graenseindikator": True,
                },
                "tiltidspunkt": {"tidsstempeldatotid": "infinity"},
                "livscykluskode": "Rettet",
                "brugerref": "42c432e8-9c4a-11e6-9f62-873cf34a735f",
                "attributter": {
                    "klasseegenskaber": [
                        {
                            "brugervendtnoegle": not_published_name,
                            "omfang": "TEXT",
                            "titel": not_published_name,
                            "virkning": {
                                "from": "1910-01-01 00:00:00+01",
                                "to": "infinity",
                                "from_included": True,
                                "to_included": False,
                            },
                        },
                        {
                            "brugervendtnoegle": "Projektgruppemedlem",
                            "omfang": "TEXT",
                            "titel": "Projektgruppemedlem",
                            "virkning": {
                                "from": "1900-01-01 01:00:00+01",
                                "to": "1910-01-01 00:00:00+01",
                                "from_included": True,
                                "to_included": False,
                            },
                        },
                    ]
                },
                "tilstande": {
                    "klassepubliceret": [
                        {
                            "virkning": {
                                "from": "1900-01-01 01:00:00+01",
                                "to": "1910-01-01 00:00:00+01",
                                "from_included": True,
                                "to_included": False,
                            },
                            "publiceret": "Publiceret",
                        },
                        {
                            "virkning": {
                                "from": "1910-01-01 00:00:00+01",
                                "to": "infinity",
                                "from_included": True,
                                "to_included": False,
                            },
                            "publiceret": not_published_state,
                        },
                    ]
                },
                "relationer": {
                    "ansvarlig": [
                        {
                            "virkning": {
                                "from": "1900-01-01 01:00:00+01",
                                "to": "infinity",
                                "from_included": True,
                                "to_included": False,
                            },
                            "uuid": "3b866d97-0b1f-48e0-8078-686d96f430b3",
                            "objekttype": "organisation",
                        }
                    ],
                    "facet": [
                        {
                            "virkning": {
                                "from": "1900-01-01 01:00:00+01",
                                "to": "infinity",
                                "from_included": True,
                                "to_included": False,
                            },
                            "uuid": str(facet_assoc_type_uuid),
                            "objekttype": "facet",
                        }
                    ],
                },
            },
        )
    ]

    response = await get_classes(facet_uuids=[facet_assoc_type_uuid])
    mo_class = one(response)

    assert mo_class.name == not_published_name
    assert mo_class.published == not_published_state
