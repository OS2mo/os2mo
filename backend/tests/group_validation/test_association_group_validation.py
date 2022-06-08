# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Optional
from unittest import mock

import pytest
from parameterized import parameterized

from mora import mapping
from mora.exceptions import HTTPException
from mora.handler.impl.association import AssociationReader
from mora.service.association import _ITAssociationGroupValidation
from mora.service.association import AssociationRequestHandler
from mora.service.association import ITAssociationPrimaryGroupValidation
from mora.service.association import ITAssociationUniqueGroupValidation
from mora.service.handlers import RequestType


class TestITAssociationGroupValidationBase:
    @parameterized.expand(
        [
            (None, None),
            ({}, None),
            ({mapping.IT: None}, None),
            ({mapping.IT: []}, None),
            ({mapping.IT: [{}]}, None),
            ({mapping.IT: [{mapping.UUID: "it-user-uuid"}]}, None),
            (
                {mapping.IT: [{mapping.UUID: "it-user-uuid", mapping.ITSYSTEM: {}}]},
                None,
            ),
            (
                {
                    mapping.IT: [
                        {
                            mapping.UUID: "it-user-uuid",
                            mapping.ITSYSTEM: {mapping.UUID: "it-system-uuid"},
                        },
                    ],
                    mapping.PRIMARY: {mapping.USER_KEY: mapping.PRIMARY},
                },
                {
                    "employee_uuid": None,
                    "org_unit_uuid": None,
                    "it_user_uuid": "it-user-uuid",
                    "it_system_uuid": "it-system-uuid",
                    "is_primary": True,
                },
            ),
        ]
    )
    def test_get_validation_item_from_mo_object(
        self, mo_object: dict, expected_result: Optional[dict]
    ):
        actual_result = (
            _ITAssociationGroupValidation.get_validation_item_from_mo_object(mo_object)
        )
        assert actual_result == expected_result

    def test_get_mo_object_reading_handler(self):
        handler = _ITAssociationGroupValidation.get_mo_object_reading_handler()
        assert isinstance(handler, AssociationReader)


class TestITAssociationUniqueGroupValidation:
    def test_validate_additional_object(self):
        obj = {"employee_uuid": "uuid", "org_unit_uuid": "uuid", "it_user_uuid": "uuid"}
        validation = ITAssociationUniqueGroupValidation([obj])
        with pytest.raises(HTTPException):
            validation.add_validation_item(obj).validate()


class TestITAssociationPrimaryGroupValidation:
    def test_validate_additional_object(self):
        obj = {"it_system_uuid": "uuid", "is_primary": True}
        validation = ITAssociationPrimaryGroupValidation([obj])
        with pytest.raises(HTTPException):
            validation.add_validation_item(obj).validate()


class TestAssociationRequestHandlerGroupValidation:
    @parameterized.expand(
        [
            (mapping.PRIMARY, True),
            ("not-primary", False),
        ]
    )
    @pytest.mark.asyncio
    async def test_is_class_primary(self, primary_class_user_key, expected_result):
        handler = AssociationRequestHandler({}, RequestType.CREATE)
        mock_get = mock.AsyncMock(
            return_value={mapping.USER_KEY: primary_class_user_key}
        )
        with mock.patch("mora.service.association.get_one_class", mock_get):
            actual_result = await handler._is_class_primary("primary-class-uuid")
            assert actual_result == expected_result

    @pytest.mark.asyncio
    async def test_get_it_system_uuid(self):
        handler = AssociationRequestHandler({}, RequestType.CREATE)
        expected_it_system_uuid = "it-system-uuid"
        it_systems = [{mapping.ITSYSTEM: {mapping.UUID: expected_it_system_uuid}}]
        mock_get = mock.AsyncMock(return_value=it_systems)
        with mock.patch("mora.handler.impl.it.ItSystemBindingReader.get", mock_get):
            actual_it_system_uuid = await handler._get_it_system_uuid("it-user-uuid")
            assert actual_it_system_uuid == expected_it_system_uuid
