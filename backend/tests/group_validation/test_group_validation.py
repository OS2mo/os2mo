# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest import mock

import pytest
from parameterized import parameterized

from mora.exceptions import ErrorCodes
from mora.exceptions import HTTPException
from mora.handler.reading import ReadingHandler
from mora.service.validation.models import GroupValidation


class TestGroupValidationConstructors:
    _mock_validation_item = {"foo": "bar"}

    def test_from_requests(self):
        requests = [{}]
        with self._mock_get_validation_item_from_mo_object():
            instance = GroupValidation.from_requests(requests)
            assert instance.validation_items == [self._mock_validation_item]

    @pytest.mark.asyncio
    async def test_from_mo_objects(self):
        search_fields = {}
        with self._mock_get_validation_item_from_mo_object():
            with self._mock_get_mo_object_reading_handler():
                instance = await GroupValidation.from_mo_objects(search_fields)
                assert instance.validation_items == [self._mock_validation_item]

    def _mock_get_validation_item_from_mo_object(self):
        return mock.patch.object(
            GroupValidation,
            "get_validation_item_from_mo_object",
            return_value=self._mock_validation_item,
        )

    def _mock_get_mo_object_reading_handler(self):
        # Mock `ReadingHandler` instance whose `.get` method always returns the same
        # "MO object".
        mock_reading_handler = mock.Mock(spec=ReadingHandler)
        mock_reading_handler.get = mock.AsyncMock(return_value={"mo": "object"})
        return mock.patch.object(
            GroupValidation,
            "get_mo_object_reading_handler",
            return_value=mock_reading_handler,
        )


class TestGroupValidationStubs:
    def test_not_implemented_stubs(self):
        with pytest.raises(NotImplementedError):
            GroupValidation.get_validation_item_from_mo_object({})
        with pytest.raises(NotImplementedError):
            GroupValidation.get_mo_object_reading_handler()


class TestGroupValidation:
    _initial_validation_items = ["a"]

    @parameterized.expand(
        [
            # 1. No `obj` passed to `validate`
            (None, _initial_validation_items),
            # 2. An `obj` passed to `validate`
            ("b", _initial_validation_items + ["b"]),
        ]
    )
    def test_validate(self, obj, expected_validation_items):
        # Before: validation items consist of the one item given by our dummy class
        instance = GroupValidation(self._initial_validation_items)
        assert instance.validation_items == self._initial_validation_items
        # After: validation items consist of our dummy class item, plus any `obj` given
        instance.validate(obj=obj)
        assert instance.validation_items == expected_validation_items

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
