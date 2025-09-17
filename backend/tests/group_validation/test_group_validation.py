# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from operator import itemgetter

import pytest
from mora.exceptions import ErrorCodes
from mora.exceptions import HTTPException
from mora.service.validation.models import GroupValidation
from parameterized import parameterized


class TestGroupValidationConstructors:
    _mock_validation_item = {"foo": "bar"}

    async def test_from_requests(self, monkeypatch):
        requests = [{}]
        self._monkeypatch_get_validation_item_from_mo_object(monkeypatch)
        instance = await GroupValidation.from_requests(requests)
        assert instance.validation_items == [self._mock_validation_item]

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

    def _monkeypatch_get_validation_item_from_mo_object(self, monkeypatch) -> None:
        async def mock_impl(*args):
            return [self._mock_validation_item]

        monkeypatch.setattr(
            GroupValidation,
            "get_validation_items_from_mo_object",
            mock_impl,
        )


class TestGroupValidationStubs:
    async def test_not_implemented_stubs(self):
        with pytest.raises(NotImplementedError):
            await GroupValidation.get_validation_items_from_mo_object({})
        with pytest.raises(NotImplementedError):
            GroupValidation.get_mo_object_reading_handler()


class TestGroupValidation:
    _initial_validation_items = [{"uuid": "a", "foo": "bar"}]
    _additional_object = {"uuid": "b", "foo": "baz"}
    _updated_object = {"uuid": "a", "foo": "baz"}

    def test_validate_additional_object(self) -> None:
        # Create an initial `GroupValidation` instance of one validation item
        instance = GroupValidation(self._initial_validation_items)
        assert instance.validation_items == self._initial_validation_items
        # Adding another validation item returns a copy of the initial instance
        instance_copy = instance.add_validation_item(self._additional_object)
        assert instance_copy.validation_items == (
            self._initial_validation_items + [self._additional_object]
        )
        assert instance is not instance_copy

    def test_validate_updated_object(self) -> None:
        # Create an initial `GroupValidation` instance of one validation item
        instance = GroupValidation(self._initial_validation_items)
        assert instance.validation_items == self._initial_validation_items
        # Updating a validation item returns a copy of the initial instance, where the
        # item has been replaced.
        instance_copy = instance.update_validation_item("a", self._updated_object)
        assert instance_copy.validation_items == [self._updated_object]
        assert instance is not instance_copy

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
    ) -> None:
        def _act() -> None:
            instance = GroupValidation(validation_items)
            instance.validate_unique_constraint(
                ["foo"],  # field names of unique constraint
                ErrorCodes.V_MISSING_REQUIRED_VALUE,  # any member of `ErrorCodes` is ok
            )

        self._assert_conditional_exception(_act, expected_exception)

    @parameterized.expand(
        [
            # 1. Only one "foo" of value "bar" - no exception raised
            ([{"foo": "bar"}, {"foo": "baz"}], None),
            # 2. More than one "foo" of value "bar" - exception raised
            ([{"foo": "bar"}, {"foo": "baz"}], None),
        ]
    )
    def test_validate_at_most_one(
        self, validation_items: list[dict], expected_exception: Exception
    ) -> None:
        def _act() -> None:
            instance = GroupValidation(validation_items)
            instance.validate_at_most_one(itemgetter("foo"), lambda val: val == "baz")

    def _assert_conditional_exception(
        self, func: Callable, exception: Exception | None
    ) -> None:
        if exception:
            with pytest.raises(exception):
                func()
        else:
            assert func() is None
