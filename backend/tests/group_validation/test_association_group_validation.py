# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Optional
from unittest import mock
from uuid import uuid4

import pytest

from mora import mapping
from mora.exceptions import HTTPException
from mora.handler.impl.association import AssociationReader
from mora.service.association import _ITAssociationGroupValidation
from mora.service.association import AssociationRequestHandler
from mora.service.association import ITAssociationPrimaryGroupValidation
from mora.service.association import ITAssociationUniqueGroupValidation
from mora.service.handlers import RequestType

_association_uuid = str(uuid4())


@pytest.mark.parametrize(
    "mo_object,expected_result",
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
                mapping.IT: [
                    {
                        mapping.UUID: "it-user-uuid",
                        mapping.ITSYSTEM: {mapping.UUID: "it-system-uuid"},
                    },
                ],
                mapping.PRIMARY: {mapping.UUID: str(uuid4())},
            },
            [
                {
                    "uuid": _association_uuid,
                    "employee_uuid": None,
                    "org_unit_uuid": None,
                    "it_user_uuid": "it-user-uuid",
                    "it_system_uuid": "it-system-uuid",
                    "is_primary": True,
                },
            ],
        ),
    ],
)
async def test_get_validation_item_from_mo_object(
    mo_object: dict, expected_result: Optional[dict]
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


def test_get_mo_object_reading_handler():
    handler = _ITAssociationGroupValidation.get_mo_object_reading_handler()
    assert isinstance(handler, AssociationReader)


def test_it_association_unique_validate_additional_object():
    obj = {"employee_uuid": "uuid", "org_unit_uuid": "uuid", "it_user_uuid": "uuid"}
    validation = ITAssociationUniqueGroupValidation([obj])
    with pytest.raises(HTTPException):
        validation.add_validation_item(obj).validate()


def test_it_association_primary_validate_additional_object():
    obj = {"it_system_uuid": "uuid", "is_primary": True}
    validation = ITAssociationPrimaryGroupValidation([obj])
    with pytest.raises(HTTPException):
        validation.add_validation_item(obj).validate()


async def test_get_it_system_uuid():
    handler = AssociationRequestHandler({}, RequestType.CREATE)
    expected_it_system_uuid = "it-system-uuid"
    it_systems = [{mapping.ITSYSTEM: {mapping.UUID: expected_it_system_uuid}}]
    mock_get = mock.AsyncMock(return_value=it_systems)
    with mock.patch("mora.handler.impl.it.ItSystemBindingReader.get", mock_get):
        actual_it_system_uuid = await handler._get_it_system_uuid("it-user-uuid")
        assert actual_it_system_uuid == expected_it_system_uuid
