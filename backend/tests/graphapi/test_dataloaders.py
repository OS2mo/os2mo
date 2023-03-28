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
from mora.graphapi.versions.latest.dataloaders import (
    format_lora_results_only_newest_relevant_lists,
)
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

lora_class_multiple_attrs_and_states = {
    "brugerref": "00000000-0000-0000-0000-000000000000",
    "fratidspunkt": {
        "tidsstempeldatotid": "1900-01-01 01:00:00+01",
        "graenseindikator": True,
    },
    "tiltidspunkt": {"tidsstempeldatotid": "infinity"},
    "livscykluskode": "Rettet",
    "attributter": {
        "klasseegenskaber": [
            {
                "brugervendtnoegle": "-",
                "omfang": "TEXT",
                "titel": "-",
                "virkning": {
                    "from": "1910-01-01 00:00:00+01",
                    "to": "infinity",
                },
            },
            {
                "brugervendtnoegle": "Gruppemedlem",
                "omfang": "TEXT",
                "titel": "Gruppemedlem",
                "virkning": {
                    "from": "1900-01-01 01:00:00+01",
                    "to": "1910-01-01 00:00:00+01",
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
                },
                "publiceret": "Publiceret",
            },
            {
                "virkning": {
                    "from": "1910-01-01 00:00:00+01",
                    "to": "infinity",
                },
                "publiceret": "IkkePubliceret",
            },
        ]
    },
    "relationer": {
        "ansvarlig": [
            {
                "virkning": {
                    "from": "1900-01-01 01:00:00+01",
                    "to": "infinity",
                },
                "uuid": "00000000-0000-0000-0000-000000000000",
                "objekttype": "organisation",
            },
        ],
        "facet": [
            {
                "virkning": {
                    "from": "1900-01-01 01:00:00+01",
                    "to": "infinity",
                },
                "uuid": "00000000-0000-0000-0000-000000000000",
                "objekttype": "facet",
            }
        ],
    },
}


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
async def test_get_classes_formatted(mock_get_all):
    lora_obj_uuid = lora_class_multiple_attrs_and_states["brugerref"]
    mock_get_all.return_value = [(lora_obj_uuid, lora_class_multiple_attrs_and_states)]

    response = await dataloaders.get_classes(facet_uuids=[uuid.UUID(lora_obj_uuid)])
    mo_class = one(response)

    assert mo_class.name == "-"
    assert mo_class.published == "IkkePubliceret"


def test_format_lora_results_only_newest_relevant_lists_empty():
    assert list(format_lora_results_only_newest_relevant_lists([], {})) == []


def test_format_lora_results_only_newest_relevant_lists_multiple_relevant_lists():
    relevant_lists = {
        "attributter": ("klasseegenskaber",),
        "tilstande": ("klassepubliceret",),
        "relationer": ("ejer", "ansvarlig", "facet"),
    }

    lora_results = [
        (
            "00000000-0000-0000-0000-000000000000",
            lora_class_multiple_attrs_and_states,
        ),
        (
            "00000000-0000-0000-0000-000000000001",
            {
                **lora_class_multiple_attrs_and_states,
                "brugerref": "00000000-0000-0000-0000-000000000001",
                "attributter": {
                    "klasseegenskaber": [
                        {
                            "brugervendtnoegle": "Gruppemedlem",
                            "omfang": "TEXT",
                            "titel": "Gruppemedlem",
                            "virkning": {
                                "from": "1900-01-01 01:00:00+01",
                                "to": "1910-01-01 00:00:00+01",
                            },
                        }
                    ]
                },
                "tilstande": {
                    "klassepubliceret": [
                        {
                            "virkning": {
                                "from": "1900-01-01 01:00:00+01",
                                "to": "1910-01-01 00:00:00+01",
                            },
                            "publiceret": "Publiceret",
                        },
                    ]
                },
            },
        ),
    ]
    exptected_after_format = [
        (
            "00000000-0000-0000-0000-000000000000",
            {
                **lora_class_multiple_attrs_and_states,
                "attributter": {
                    "klasseegenskaber": [
                        {
                            "brugervendtnoegle": "-",
                            "omfang": "TEXT",
                            "titel": "-",
                            "virkning": {
                                "from": "1910-01-01 00:00:00+01",
                                "to": "infinity",
                            },
                        },
                    ]
                },
                "tilstande": {
                    "klassepubliceret": [
                        {
                            "virkning": {
                                "from": "1910-01-01 00:00:00+01",
                                "to": "infinity",
                            },
                            "publiceret": "IkkePubliceret",
                        }
                    ]
                },
            },
        ),
        (
            "00000000-0000-0000-0000-000000000001",
            {
                **lora_class_multiple_attrs_and_states,
                "brugerref": "00000000-0000-0000-0000-000000000001",
                "attributter": {
                    "klasseegenskaber": [
                        {
                            "brugervendtnoegle": "Gruppemedlem",
                            "omfang": "TEXT",
                            "titel": "Gruppemedlem",
                            "virkning": {
                                "from": "1900-01-01 01:00:00+01",
                                "to": "1910-01-01 00:00:00+01",
                            },
                        }
                    ]
                },
                "tilstande": {
                    "klassepubliceret": [
                        {
                            "virkning": {
                                "from": "1900-01-01 01:00:00+01",
                                "to": "1910-01-01 00:00:00+01",
                            },
                            "publiceret": "Publiceret",
                        },
                    ]
                },
            },
        ),
    ]

    assert (
        list(
            format_lora_results_only_newest_relevant_lists(lora_results, relevant_lists)
        )
        == exptected_after_format
    )


def test_format_lora_results_only_newest_relevant_lists_single_relevant_lists():
    relevant_lists = {"attributter": ("klasseegenskaber",)}

    lora_results = [
        (
            "00000000-0000-0000-0000-000000000000",
            lora_class_multiple_attrs_and_states,
        )
    ]

    exptected_after_format = [
        (
            "00000000-0000-0000-0000-000000000000",
            {
                **lora_class_multiple_attrs_and_states,
                "attributter": {
                    "klasseegenskaber": [
                        {
                            "brugervendtnoegle": "-",
                            "omfang": "TEXT",
                            "titel": "-",
                            "virkning": {
                                "from": "1910-01-01 00:00:00+01",
                                "to": "infinity",
                            },
                        },
                    ]
                },
            },
        )
    ]

    assert (
        list(
            format_lora_results_only_newest_relevant_lists(lora_results, relevant_lists)
        )
        == exptected_after_format
    )
