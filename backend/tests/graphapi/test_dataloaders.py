# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests of dataloaders used in the GraphQL implementation."""

import pytest
from hypothesis import given
from mora.graphapi.versions.latest import dataloaders
from mora.graphapi.versions.latest.dataloaders import MOModel
from mora.graphapi.versions.latest.graphql_utils import LoadKey
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
from mora.graphapi.versions.latest.schema import RoleBindingRead
from pytest import MonkeyPatch

from .strategies import data_with_uuids_strat

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
    RoleBindingRead,
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


@pytest.fixture(scope="session")
def patch_loader():
    """Fixture to patch dataloaders for mocks.

    It looks a little weird, being a function yielding a function which returns
    a function. However, this is necessary in order to be able to use the fixture
    with extra parameters.
    """

    def patcher(data: list[MOModel]):
        # If our dataloader functions were sync, we could have used a lambda directly
        # when monkeypatching. They are async, however, and as such we need to mock
        # using an async function.
        async def _patcher(*args, **kwargs):
            return data

        return _patcher

    yield patcher


@given(test_data=data_with_uuids_strat(models))
async def test_load(test_data, patch_loader):
    """Test load of models."""
    # Sample data & UUIDs
    model, data, uuids, _ = test_data
    keys = [LoadKey(uuid, None, None, None) for uuid in uuids]

    # Patch loader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "get_role_type_by_uuid", patch_loader(data))
        result = await dataloaders.load_mo(keys, model)

    # We expect as many results as there are UUIDs passed to the function.
    # Additionally, the result must be an improper subset of the test data.
    assert len(result) == len(uuids)
    data_map = {model.uuid: model for model in data}
    result_map = {model.uuid: model for group in result for model in group}
    assert result_map.items() <= data_map.items()


@given(test_data=data_with_uuids_strat(models))
async def test_load_nonexistent(test_data, patch_loader):
    """Test load of UUIDs that do not exist in data, including the empty list."""
    # Sample data & UUIDs
    model, data, _, other_uuids = test_data
    keys = [LoadKey(uuid, None, None, None) for uuid in other_uuids]

    # Patch loader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "get_role_type_by_uuid", patch_loader(data))
        result = await dataloaders.load_mo(keys, model)

    # Again, we expect as many results as there are UUIDs passed to the function.
    assert len(result) == len(other_uuids)
    if other_uuids:
        assert result == [[] for _ in other_uuids]
    else:
        assert result == []
