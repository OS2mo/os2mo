# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest import mock
from uuid import uuid4

import pytest
from mora import mapping
from mora.exceptions import HTTPException
from mora.handler.impl.association import AssociationReader
from mora.service.association import ITAssociationPrimaryGroupValidation
from mora.service.association import ITAssociationUniqueGroupValidation
from mora.service.association import _ITAssociationGroupValidation
from parameterized import parameterized


class TestITAssociationGroupValidationBase:
    _association_uuid = str(uuid4())

    @parameterized.expand(
        [
            # A number of insufficient payloads, which cause the method to return an
            # empty list.
            (None, []),
            ({}, []),
            ({mapping.IT: None}, []),
            ({mapping.IT: []}, []),
            ({mapping.IT: [{}]}, []),
            ({mapping.IT: [{mapping.UUID: "it-user-uuid"}]}, []),
            (
                {mapping.IT: [{mapping.UUID: "it-user-uuid", mapping.ITSYSTEM: {}}]},
                [],
            ),
            # Minimal valid payload
            (
                {
                    mapping.UUID: _association_uuid,
                    mapping.IT: [{mapping.UUID: "it-user-uuid"}],
                    mapping.PRIMARY: {mapping.UUID: str(uuid4())},
                },
                [
                    {
                        "uuid": _association_uuid,
                        "employee_uuid": None,
                        "org_unit_uuid": None,
                        "it_user_uuid": "it-user-uuid",
                        "is_primary": True,
                    },
                ],
            ),
        ]
    )
    @pytest.mark.asyncio
    async def test_get_validation_item_from_mo_object(
        self,
        mo_object: dict,
        expected_result: dict | None,
    ):
        with mock.patch(
            "mora.service.association.get_mo_object_primary_value",
            return_value=(
                expected_result[0].get("is_primary", False)
                if expected_result != []
                else False
            ),
        ):
            actual_result = (
                await _ITAssociationGroupValidation.get_validation_items_from_mo_object(
                    mo_object
                )
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
        obj = {"it_user_uuid": "uuid", "is_primary": True}
        validation = ITAssociationPrimaryGroupValidation([obj])
        with pytest.raises(HTTPException):
            validation.add_validation_item(obj).validate()
