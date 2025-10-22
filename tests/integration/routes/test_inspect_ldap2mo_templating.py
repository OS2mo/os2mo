# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json
from unittest.mock import ANY
from uuid import UUID

import pytest
from httpx import AsyncClient
from structlog.testing import capture_logs

from mo_ldap_import_export.types import DN
from mo_ldap_import_export.types import LDAPUUID


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
        "LISTEN_TO_CHANGES_IN_MO": "False",
    }
)
async def test_mo2ldap_template_unknown(test_client: AsyncClient) -> None:
    uuid = UUID("6c7fff8f-8510-4c99-92ee-9c8548484870")  # Random UUID

    with capture_logs() as cap_logs:
        response = await test_client.get(f"/Inspect/ldap2mo/{uuid}")
        assert response.status_code == 200
        result = response.json()
        assert result is None

    events = {log["event"] for log in cap_logs}
    assert {
        "Looking for LDAP object",
        "Unable to convert LDAP UUID to DN",
    }.issubset(events)


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "CONVERSION_MAPPING": json.dumps({}),
    }
)
async def test_mo2ldap_template_no_config(
    test_client: AsyncClient, ldap_person_uuid: LDAPUUID
) -> None:
    with capture_logs() as cap_logs:
        response = await test_client.get(f"/Inspect/ldap2mo/{ldap_person_uuid}")
        assert response.status_code == 200
        result = response.json()
        assert result is None

    events = {log["event"] for log in cap_logs}
    assert {
        "Looking for LDAP object",
        "import_single_user called without mapping",
    }.issubset(events)


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "CONVERSION_MAPPING": json.dumps({"ldap_to_mo": {}}),
    }
)
async def test_mo2ldap_template_empty_config(
    test_client: AsyncClient, ldap_person_uuid: LDAPUUID
) -> None:
    with capture_logs() as cap_logs:
        response = await test_client.get(f"/Inspect/ldap2mo/{ldap_person_uuid}")
        assert response.status_code == 200
        result = response.json()
        assert result is None

    events = {log["event"] for log in cap_logs}
    assert {
        "Looking for LDAP object",
        "import_single_user called without mapping",
    }.issubset(events)


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "CONVERSION_MAPPING": json.dumps(
            {
                "ldap_to_mo": {
                    "Employee": {
                        "objectClass": "Employee",
                        "_import_to_mo_": "false",
                        "_ldap_attributes_": [],
                        "uuid": "{{ skip_if_none(None) }}",
                    }
                }
            }
        ),
    }
)
async def test_mo2ldap_template_skip_config(
    test_client: AsyncClient, ldap_person_uuid: LDAPUUID
) -> None:
    with capture_logs() as cap_logs:
        response = await test_client.get(f"/Inspect/ldap2mo/{ldap_person_uuid}")
        assert response.status_code == 200
        result = response.json()
        assert result is None

    events = {log["event"] for log in cap_logs}
    assert {
        "Looking for LDAP object",
        "Found DN",
        "No matching employee",
        "Employee not found in MO, and not configured to create it",
    }.issubset(events)


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "CONVERSION_MAPPING": json.dumps(
            {
                "ldap_to_mo": {
                    "Employee": {
                        "objectClass": "Employee",
                        "_import_to_mo_": "true",
                        "_ldap_attributes_": [],
                        "uuid": "{{ skip_if_none(None) }}",
                    }
                }
            }
        ),
    }
)
async def test_mo2ldap_template_skip_config_create(
    test_client: AsyncClient, ldap_person_uuid: LDAPUUID
) -> None:
    with capture_logs() as cap_logs:
        response = await test_client.get(f"/Inspect/ldap2mo/{ldap_person_uuid}")
        assert response.status_code == 200
        result = response.json()
        assert result is None

    events = {log["event"] for log in cap_logs}
    assert {
        "Looking for LDAP object",
        "Found DN",
        "No matching employee",
        "Employee not found, but configured to create it",
        "Employee not found in MO, generated UUID",
        "No discriminator filter set, not filtering",
        "Skipping object",
    }.issubset(events)


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "CONVERSION_MAPPING": json.dumps(
            {
                "ldap_to_mo": {
                    "Employee": {
                        "objectClass": "Employee",
                        "_import_to_mo_": "true",
                        "_ldap_attributes_": [],
                        "uuid": "{{ employee_uuid }}",
                    }
                }
            }
        ),
    }
)
async def test_mo2ldap_template_create(
    test_client: AsyncClient, ldap_person_dn: DN, ldap_person_uuid: LDAPUUID
) -> None:
    with capture_logs() as cap_logs:
        response = await test_client.get(f"/Inspect/ldap2mo/{ldap_person_uuid}")
        assert response.status_code == 451
        result = response.json()
        assert result == {
            "detail": {
                "message": "Would have uploaded changes to MO",
                "dn": ldap_person_dn,
                "verb": "Verb.CREATE",
                "obj": {
                    "uuid": ANY,
                    "user_key": ANY,
                    "given_name": None,
                    "surname": None,
                    "cpr_number": None,
                    "seniority": None,
                    "nickname_given_name": "",
                    "nickname_surname": "",
                },
            }
        }

    events = {log["event"] for log in cap_logs}
    assert {
        "Looking for LDAP object",
        "Found DN",
        "No matching employee",
        "Employee not found, but configured to create it",
        "Employee not found in MO, generated UUID",
        "No discriminator filter set, not filtering",
        "Importing object",
    }.issubset(events)


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "CONVERSION_MAPPING": json.dumps(
            {
                "ldap_to_mo": {
                    "Employee": {
                        "objectClass": "Employee",
                        "_import_to_mo_": "true",
                        "_ldap_attributes_": [],
                        "uuid": "{{ employee_uuid }}",
                    }
                }
            }
        ),
    }
)
@pytest.mark.usefixtures("mo_person")
async def test_mo2ldap_template_existing_noop(
    test_client: AsyncClient, ldap_person_uuid: LDAPUUID
) -> None:
    with capture_logs() as cap_logs:
        response = await test_client.get(f"/Inspect/ldap2mo/{ldap_person_uuid}")
        assert response.status_code == 200
        result = response.json()
        assert result is None

    events = {log["event"] for log in cap_logs}
    assert {
        "Looking for LDAP object",
        "Found DN",
        "Found employee via CPR matching",
        "No discriminator filter set, not filtering",
        "Converted object is identical to existing object, skipping",
        "No converted objects after formatting",
    }.issubset(events)


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "CONVERSION_MAPPING": json.dumps(
            {
                "ldap_to_mo": {
                    "Employee": {
                        "objectClass": "Employee",
                        "_import_to_mo_": "true",
                        "_ldap_attributes_": [],
                        "uuid": "{{ employee_uuid }}",
                        "given_name": "Cleo",
                        "surname": "Ashton",
                    }
                }
            }
        ),
    }
)
async def test_mo2ldap_template_existing_change(
    test_client: AsyncClient,
    mo_person: UUID,
    ldap_person_dn: DN,
    ldap_person_uuid: LDAPUUID,
) -> None:
    with capture_logs() as cap_logs:
        response = await test_client.get(f"/Inspect/ldap2mo/{ldap_person_uuid}")
        assert response.status_code == 451
        result = response.json()
        assert result == {
            "detail": {
                "message": "Would have uploaded changes to MO",
                "dn": ldap_person_dn,
                "verb": "Verb.EDIT",
                "obj": {
                    "uuid": str(mo_person),
                    "user_key": str(mo_person),
                    "given_name": "Cleo",
                    "surname": "Ashton",
                    "cpr_number": "2108613133",
                    "seniority": None,
                    "nickname_given_name": "",
                    "nickname_surname": "",
                },
            }
        }

    events = {log["event"] for log in cap_logs}
    assert {
        "Looking for LDAP object",
        "Found DN",
        "Found employee via CPR matching",
        "No discriminator filter set, not filtering",
        "Setting values on upload dict",
        "Importing object",
    }.issubset(events)
