# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from parameterized import parameterized

from mora.exceptions import ErrorCodes
from mora.exceptions import HTTPException
from mora.service.validation.models import GroupValidation


class TestGroupValidationConstructors:
    _mock_validation_item = {"foo": "bar"}

    def test_from_requests(self, monkeypatch):
        requests = [{}]
        self._monkeypatch_get_validation_item_from_mo_object(monkeypatch)
        instance = GroupValidation.from_requests(requests)
        assert instance.validation_items == [self._mock_validation_item]

    @pytest.mark.asyncio
    async def test_from_mo_objects(self, monkeypatch):
        class _MockReadingHandler:
            async def get(self, *args, **kwargs):
                return {"mo": "object"}

        search_fields = {}

        self._monkeypatch_get_validation_item_from_mo_object(monkeypatch)
        monkeypatch.setattr(
            GroupValidation, "get_mo_object_reading_handler", _MockReadingHandler
        )
        instance = await GroupValidation.from_mo_objects(search_fields)
        assert instance.validation_items == [self._mock_validation_item]

    def _monkeypatch_get_validation_item_from_mo_object(self, monkeypatch):
        monkeypatch.setattr(
            GroupValidation,
            "get_validation_item_from_mo_object",
            lambda *args: self._mock_validation_item,
        )


class TestGroupValidationStubs:
    def test_not_implemented_stubs(self):
        with pytest.raises(NotImplementedError):
            GroupValidation.get_validation_item_from_mo_object({})
        with pytest.raises(NotImplementedError):
            GroupValidation.get_mo_object_reading_handler()


class TestGroupValidation:
    _initial_validation_items = [{"a": "a"}]
    _additional_object = {"b": "b"}

    def test_validate_additional_object(self, monkeypatch):
        # Before: validation items consist of the initial items
        instance = GroupValidation(self._initial_validation_items)
        assert instance.validation_items == self._initial_validation_items
        monkeypatch.setattr(instance, "validate", lambda *args: None)
        # After: validation items consist of initial items, plus an additional item
        instance.validate_additional_object(self._additional_object)
        assert instance.validation_items == (
            self._initial_validation_items + [self._additional_object]
        )

    @parameterized.expand(
        [
            # 1. No duplicates - no exception raised
            ([{"foo": "bar"}], None),
            # 2. Duplicates - exception raised
            ([{"foo": "bar"}, {"foo": "bar"}], HTTPException),
        ]
    )
    def test_validate_unique_constraint(
        self, validation_items: list[dict], expected_exception: Exception
    ):
        instance = GroupValidation(validation_items)
        field_names = ["foo"]
        error = ErrorCodes.V_MISSING_REQUIRED_VALUE  # any member of `ErrorCodes` is ok
        if expected_exception:
            with pytest.raises(expected_exception):
                instance.validate_unique_constraint(field_names, error)
        else:
            assert instance.validate_unique_constraint(field_names, error) is None
