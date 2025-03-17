# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import uuid4

import pytest

from mo_ldap_import_export.types import LDAPUUID


def test_type_construction() -> None:
    uuid = uuid4()
    ldap_uuid = LDAPUUID(str(uuid))
    assert ldap_uuid == uuid


def test_type_construction_error() -> None:
    with pytest.raises(ValueError) as exc_info:
        LDAPUUID("hej")
    assert "badly formed hexadecimal UUID string" in str(exc_info.value)
