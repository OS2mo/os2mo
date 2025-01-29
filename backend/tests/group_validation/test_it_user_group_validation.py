# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest import mock
from uuid import uuid4

import pytest
from hypothesis import given
from hypothesis import strategies as st
from mora import mapping
from mora.exceptions import HTTPException
from mora.handler.impl.it import ItSystemBindingReader
from mora.service.itsystem import ITUserPrimaryGroupValidation
from mora.service.itsystem import ITUserUniqueGroupValidation
from mora.service.itsystem import _ITUserGroupValidation


class TestITUserGroupValidationBase:
    _it_user_uuid = str(uuid4())
    _mo_uuid = st.fixed_dictionaries({mapping.UUID: st.uuids().map(str)})

    @given(
        st.fixed_dictionaries(
            {
                mapping.PERSON: _mo_uuid,
                mapping.ITSYSTEM: _mo_uuid,
                mapping.ENGAGEMENT: _mo_uuid | st.none(),
                mapping.PRIMARY: _mo_uuid,
                mapping.USER_KEY: st.text(),
            },
            optional={mapping.UUID: st.none() | st.uuids().map(str)},
        )
    )
    async def test_get_validation_item_from_mo_object(self, mo_object: dict):
        with mock.patch("mora.service.facet.get_one_class", mock.AsyncMock()):
            items = await _ITUserGroupValidation.get_validation_items_from_mo_object(
                mo_object
            )
            assert isinstance(items, list)
            assert len(items) == 1
            assert isinstance(items[0]["uuid"], (str, type(None)))
            assert isinstance(items[0]["employee_uuid"], str)
            assert isinstance(items[0]["it_system_uuid"], str)
            assert isinstance(items[0]["engagement_uuid"], (str, type(None)))
            assert isinstance(items[0]["it_user_username"], str)
            assert isinstance(items[0]["is_primary"], bool)

    def test_get_mo_object_reading_handler(self):
        handler = _ITUserGroupValidation.get_mo_object_reading_handler()
        assert isinstance(handler, ItSystemBindingReader)


class TestITUserUniqueGroupValidation:
    def test_validate_additional_object(self):
        obj = {
            "employee_uuid": "uuid",
            "it_system_uuid": "uuid",
            "engagement_uuid": "uuid",
            "it_user_username": "uuid",
        }
        validation = ITUserUniqueGroupValidation([obj])
        with pytest.raises(HTTPException):
            validation.add_validation_item(obj).validate()


class TestITAssociationPrimaryGroupValidation:
    def test_validate_additional_object(self):
        obj = {"it_system_uuid": "uuid", "is_primary": True}
        validation = ITUserPrimaryGroupValidation([obj])
        with pytest.raises(HTTPException):
            validation.add_validation_item(obj).validate()
