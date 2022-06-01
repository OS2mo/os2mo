# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from parameterized import parameterized

from mora.exceptions import ErrorCodes
from mora.exceptions import HTTPException
from mora.handler.reading import ReadingHandler
from mora.mapping import RequestType
from mora.service.employee import EmployeeRequestHandler
from mora.service.validation.models import GroupValidation


class _MockReadingHandler(ReadingHandler):
    _mo_object = {"mo": "object"}

    @classmethod
    async def get(cls, *args, **kwargs):
        return [cls._mo_object]


class _DummyGroupValidation(GroupValidation):
    _fixed_validation_item = {"foo": "bar"}

    @classmethod
    def get_validation_item_from_mo_object(cls, mo_object: dict):
        return cls._fixed_validation_item

    @classmethod
    def get_mo_object_reading_handler(cls) -> "ReadingHandler":
        return _MockReadingHandler()


class TestGroupValidationConstructors:
    def test_from_requests(self):
        request = {}
        employee_request_handler = EmployeeRequestHandler(request, RequestType.CREATE)
        instance = _DummyGroupValidation.from_requests([employee_request_handler])
        assert instance.validation_items == [
            _DummyGroupValidation._fixed_validation_item
        ]

    @pytest.mark.asyncio
    async def test_from_mo_objects(self):
        search_fields = {}
        instance = await _DummyGroupValidation.from_mo_objects(search_fields)
        assert instance.validation_items == [
            _DummyGroupValidation._fixed_validation_item
        ]


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
