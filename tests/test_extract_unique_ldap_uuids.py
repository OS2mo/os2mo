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
from tests.integration.conftest import AnyOrder


def create_ituser(user_key: str) -> ITUser:
    return ITUser(
        user_key=user_key,
        itsystem=uuid4(),
        person=uuid4(),
        validity={"start": datetime.datetime.today()},
    )


def test_extract_unique_ldap_uuids() -> None:
    ldap_uuid_1 = str(uuid4())
    ldap_uuid_2 = str(uuid4())
    it_user_1 = create_ituser(ldap_uuid_1)
    it_user_2 = create_ituser(ldap_uuid_2)

    ldap_uuids = extract_unique_ldap_uuids([it_user_1, it_user_2])
    assert ldap_uuids == {LDAPUUID(ldap_uuid_1), LDAPUUID(ldap_uuid_2)}


def test_extract_unique_ldap_uuids_non_uuid() -> None:
    it_user = create_ituser("not_an_uuid")
    with pytest.raises(ExceptionGroup) as exc_info:
        extract_unique_ldap_uuids([it_user])
    exception = one(exc_info.value.exceptions)
    assert str(exception) == "Non UUID IT-user user-key: not_an_uuid"


def test_extract_unique_ldap_uuids_multiple_non_uuids() -> None:
    it_user_1 = create_ituser("not_an_uuid_1")
    it_user_2 = create_ituser("not_an_uuid_2")
    with pytest.raises(ExceptionGroup) as exc_info:
        extract_unique_ldap_uuids([it_user_1, it_user_2])
    exception_errors = [str(exception) for exception in exc_info.value.exceptions]
    assert AnyOrder(exception_errors) == [
        "Non UUID IT-user user-key: not_an_uuid_1",
        "Non UUID IT-user user-key: not_an_uuid_2",
    ]


def test_extract_unique_ldap_uuids_mixed() -> None:
    ldap_uuid_1 = str(uuid4())
    it_user_1 = create_ituser(ldap_uuid_1)
    it_user_2 = create_ituser("not_an_uuid")
    with pytest.raises(ExceptionGroup) as exc_info:
        extract_unique_ldap_uuids([it_user_1, it_user_2])
    exception = one(exc_info.value.exceptions)
    assert str(exception) == "Non UUID IT-user user-key: not_an_uuid"


def test_extract_unique_ldap_uuids_multiple_mixed() -> None:
    ldap_uuid_1 = str(uuid4())
    ldap_uuid_2 = str(uuid4())
    it_user_1 = create_ituser(ldap_uuid_1)
    it_user_2 = create_ituser(ldap_uuid_2)
    it_user_3 = create_ituser("not_an_uuid_1")
    it_user_4 = create_ituser("not_an_uuid_2")
    with pytest.raises(ExceptionGroup) as exc_info:
        extract_unique_ldap_uuids([it_user_1, it_user_2, it_user_3, it_user_4])
    exception_errors = [str(exception) for exception in exc_info.value.exceptions]
    assert AnyOrder(exception_errors) == [
        "Non UUID IT-user user-key: not_an_uuid_1",
        "Non UUID IT-user user-key: not_an_uuid_2",
    ]


def test_extract_unique_ldap_uuids_duplicate_non_uuids() -> None:
    it_user_1 = create_ituser("not_an_uuid")
    it_user_2 = create_ituser("not_an_uuid")
    with pytest.raises(ExceptionGroup) as exc_info:
        extract_unique_ldap_uuids([it_user_1, it_user_2])
    exception_errors = [str(exception) for exception in exc_info.value.exceptions]
    assert exception_errors == ["Non UUID IT-user user-key: not_an_uuid"]


def test_extract_unique_ldap_uuids_duplicate_mixed() -> None:
    ldap_uuid = str(uuid4())
    it_user_1 = create_ituser(ldap_uuid)
    it_user_2 = create_ituser("not_an_uuid")
    it_user_3 = create_ituser("not_an_uuid")
    with pytest.raises(ExceptionGroup) as exc_info:
        extract_unique_ldap_uuids([it_user_1, it_user_2, it_user_3])
    exception_errors = [str(exception) for exception in exc_info.value.exceptions]
    assert exception_errors == ["Non UUID IT-user user-key: not_an_uuid"]


def test_extract_unique_ldap_uuids_duplicate_uuid() -> None:
    ldap_uuid = str(uuid4())
    it_user_1 = create_ituser(ldap_uuid)
    it_user_2 = create_ituser(ldap_uuid)
    with pytest.raises(ExceptionGroup) as exc_info:
        extract_unique_ldap_uuids([it_user_1, it_user_2])
    exception = one(exc_info.value.exceptions)
    assert str(exception) == f"Duplicate UUID IT-user user-key: {ldap_uuid}"


def test_extract_unique_ldap_uuids_duplicate_uuids_mixed() -> None:
    ldap_uuid_1 = str(uuid4())
    ldap_uuid_2 = str(uuid4())
    it_user_11 = create_ituser(ldap_uuid_1)
    it_user_12 = create_ituser(ldap_uuid_1)
    it_user_2 = create_ituser(ldap_uuid_2)
    with pytest.raises(ExceptionGroup) as exc_info:
        extract_unique_ldap_uuids([it_user_11, it_user_12, it_user_2])
    exception = one(exc_info.value.exceptions)
    assert str(exception) == f"Duplicate UUID IT-user user-key: {ldap_uuid_1}"


def test_extract_unique_ldap_uuids_duplicate_uuids() -> None:
    ldap_uuid_1 = str(uuid4())
    ldap_uuid_2 = str(uuid4())
    it_user_11 = create_ituser(ldap_uuid_1)
    it_user_12 = create_ituser(ldap_uuid_1)
    it_user_21 = create_ituser(ldap_uuid_2)
    it_user_22 = create_ituser(ldap_uuid_2)
    with pytest.raises(ExceptionGroup) as exc_info:
        extract_unique_ldap_uuids([it_user_11, it_user_12, it_user_21, it_user_22])
    exception_errors = [str(exception) for exception in exc_info.value.exceptions]
    assert AnyOrder(exception_errors) == [
        f"Duplicate UUID IT-user user-key: {ldap_uuid_1}",
        f"Duplicate UUID IT-user user-key: {ldap_uuid_2}",
    ]
