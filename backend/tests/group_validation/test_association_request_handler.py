# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import AsyncMock
from unittest.mock import Mock

import pytest

from mora.service.association import AssociationRequestHandler


class TestAssociationRequestHandlerGroupValidation:
    _association_uuid = "association-uuid"
    _employee_uuid = "employee-uuid"
    _it_user_uuid = "it-user-uuid"
    _it_system_uuid = "it-system-uuid"
    _org_unit_uuid = "org-unit-uuid"

    _expected_kwargs_a = {"tilknyttedebrugere": _employee_uuid}
    _expected_kwargs_b = {
        "tilknyttedebrugere": _employee_uuid,
        "tilknyttedeenheder": _org_unit_uuid,
    }

    @pytest.mark.parametrize(
        "method_name,method_args,expected_kwargs",
        [
            # 1a. Test that `AssociationRequestHandler.validate_unique_group_on_create`
            # uses `ITAssociationUniqueGroupValidation` correctly.
            (
                "validate_unique_group_on_create",
                (_employee_uuid, _it_user_uuid),
                _expected_kwargs_a,
            ),
            # 1b. Test that `AssociationRequestHandler.validate_primary_group_on_create`
            # uses `ITAssociationPrimaryGroupValidation` correctly.
            (
                "validate_primary_group_on_create",
                (_employee_uuid, _it_user_uuid, _org_unit_uuid),
                _expected_kwargs_b,
            ),
            # 2a. Test that `AssociationRequestHandler.validate_unique_group_on_edit`
            # uses `ITAssociationUniqueGroupValidation` correctly.
            (
                "validate_unique_group_on_edit",
                (_association_uuid, _employee_uuid, _it_user_uuid, _org_unit_uuid),
                _expected_kwargs_a,
            ),
            # 2b. Test that `AssociationRequestHandler.validate_primary_group_on_edit`
            # uses `ITAssociationPrimaryGroupValidation` correctly.
            (
                "validate_primary_group_on_edit",
                (_association_uuid, _employee_uuid, _it_user_uuid),
                _expected_kwargs_a,
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_group_validation_usage(
        self,
        monkeypatch: pytest.MonkeyPatch,
        method_name: str,
        method_args: tuple[str],
        expected_kwargs: dict[str],
    ):
        # Arrange
        mock_from_mo_objects = AsyncMock(return_value=Mock())
        handler = AssociationRequestHandler(None, None)  # type: ignore
        with monkeypatch.context() as ctx:
            ctx.setattr(
                "mora.service.validation.models.GroupValidation.from_mo_objects",
                mock_from_mo_objects,
            )
            ctx.setattr(
                handler,
                "_get_it_system_uuid",
                AsyncMock(return_value=self._it_system_uuid),
            )
            method = getattr(handler, method_name)
            # Act
            await method(*method_args)
            # Assert
            mock_from_mo_objects.assert_called_once_with(expected_kwargs)
