#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
"""Tests of dataloaders used in the GraphQL implementation."""
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import pytest
from hypothesis import given
from pytest import MonkeyPatch

import mora.graphapi.dataloaders as dataloaders
from .strategies import data_strat
from .strategies import data_with_uuids_strat
from mora.graphapi.schema import AddressRead
from mora.graphapi.schema import AssociationRead
from mora.graphapi.schema import EmployeeRead
from mora.graphapi.schema import EngagementRead
from mora.graphapi.schema import ITUserRead
from mora.graphapi.schema import KLERead
from mora.graphapi.schema import LeaveRead
from mora.graphapi.schema import ManagerRead
from mora.graphapi.schema import OrganisationUnitRead
from mora.graphapi.schema import RelatedUnitRead
from mora.graphapi.schema import RoleRead

# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------

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
