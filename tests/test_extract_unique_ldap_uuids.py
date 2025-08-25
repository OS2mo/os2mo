# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=protected-access
import datetime
from uuid import uuid4

import pytest
from more_itertools import one

from mo_ldap_import_export.dataloaders import extract_unique_ldap_uuids
from mo_ldap_import_export.models import ITUser
from mo_ldap_import_export.types import LDAPUUID


def test_extract_unique_ldap_uuids() -> None:
    ldap_uuid_1 = str(uuid4())
    ldap_uuid_2 = str(uuid4())
    it_user_1 = ITUser(
        user_key=ldap_uuid_1,
        itsystem=uuid4(),
        person=uuid4(),
        validity={"start": datetime.datetime.today()},
    )
    it_user_2 = ITUser(
        user_key=ldap_uuid_2,
        itsystem=uuid4(),
        person=uuid4(),
        validity={"start": datetime.datetime.today()},
    )

    ldap_uuids = extract_unique_ldap_uuids([it_user_1, it_user_2])
    assert ldap_uuids == {LDAPUUID(ldap_uuid_1), LDAPUUID(ldap_uuid_2)}

    it_user_3 = ITUser(
        user_key="not_an_uuid",
        itsystem=uuid4(),
        person=uuid4(),
        validity={"start": datetime.datetime.today()},
    )
    with pytest.raises(ExceptionGroup) as exc_info:
        extract_unique_ldap_uuids([it_user_1, it_user_2, it_user_3])
    exception = one(exc_info.value.exceptions)
    assert str(exception) == "Non UUID IT-user user-key: not_an_uuid"
