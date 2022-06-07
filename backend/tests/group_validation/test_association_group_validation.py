# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest

from mora.exceptions import HTTPException
from mora.service.association import ITAssociationPrimaryGroupValidation
from mora.service.association import ITAssociationUniqueGroupValidation


class TestITAssociationUniqueGroupValidation:
    def test_validation(self):
        obj = {"employee_uuid": "uuid", "org_unit_uuid": "uuid", "it_user_uuid": "uuid"}
        validation = ITAssociationUniqueGroupValidation([obj])
        with pytest.raises(HTTPException):
            validation.validate(obj)


class TestITAssociationPrimaryGroupValidation:
    def test_validation(self):
        obj = {"it_system_uuid": "uuid", "is_primary": True}
        validation = ITAssociationPrimaryGroupValidation([obj])
        with pytest.raises(HTTPException):
            validation.validate(obj)
