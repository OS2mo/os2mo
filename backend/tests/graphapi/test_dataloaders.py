# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests of dataloaders used in the GraphQL implementation."""
import datetime
import uuid

import pytest
from hypothesis import given
from pytest import MonkeyPatch

from .strategies import data_strat
from .strategies import data_with_uuids_strat
from mora.graphapi.versions.latest import dataloaders
from mora.graphapi.versions.latest.dataloaders import lora_class_to_mo_class
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
from mora.util import NEGATIVE_INFINITY
from mora.util import POSITIVE_INFINITY
from ramodels.lora._shared import EffectiveTime
from ramodels.lora._shared import InfiniteDatetime
from ramodels.lora.klasse import KlasseRead
from tests.hypothesis.strats_ramodels import valid_klasse_relations

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


@given(valid_klasse_relations())
async def test_lora_class_to_mo_class_filter_attrs_states(test_data_relations):
    test_data_uuid = uuid.uuid4()

    now = datetime.datetime.now(tz=datetime.timezone.utc)
    test_data_from_dt = now - datetime.timedelta(days=5)
    test_data_to_dt = now + datetime.timedelta(days=5)
    effective_time_old = EffectiveTime(
        from_date=NEGATIVE_INFINITY, to_date=test_data_from_dt
    )
    effective_time_current = EffectiveTime(
        from_date=test_data_from_dt, to_date=POSITIVE_INFINITY
    )

    lora_class = KlasseRead(
        **{
            "uuid": test_data_uuid,
            "attributes": {
                "properties": [
                    {
                        "user_key": "some-user-key-attr-1",
                        "title": "a fancy title attr 1",
                        "effective_time": effective_time_old,
                    },
                    {
                        "user_key": "-",
                        "title": "-",
                        "effective_time": effective_time_current,
                    },
                ]
            },
            "states": {
                "published_state": [
                    {"published": "Publiceret", "effective_time": effective_time_old},
                    {
                        "published": "ikkePubliceret",
                        "effective_time": effective_time_current,
                    },
                ]
            },
            "relations": test_data_relations,
            "fratidspunkt": {
                "tidsstempeldatotid": InfiniteDatetime.from_value(test_data_from_dt),
            },
            "tiltidspunkt": {
                "tidsstempeldatotid": InfiniteDatetime.from_value(test_data_to_dt)
            },
            "life_cycle_code": "",
            "user_ref": uuid.uuid4(),
        }
    )

    result = lora_class_to_mo_class((test_data_uuid, lora_class))
    assert result.name == lora_class.attributes.properties[1].title
    assert result.user_key == lora_class.attributes.properties[1].user_key
    assert result.published == lora_class.states.published_state[1].published
