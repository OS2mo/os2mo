# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json
from unittest.mock import ANY
from uuid import UUID

import pytest
from httpx import AsyncClient

from mo_ldap_import_export.types import DN
from mo_ldap_import_export.types import LDAPUUID
from mo_ldap_import_export.utils import combine_dn_strings
from tests.integration.conftest import DN2UUID
from tests.integration.conftest import AddLdapPerson


def read_jsonl_file(filename: str) -> list[dict]:
    with open(filename) as fin:
        file_data = []
        for line in fin.readlines():
            file_data.append(json.loads(line))
        # Skip non-employees
        file_data = [
            row for row in file_data if row["message"] != "Skipping non-employee"
        ]
        return file_data


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
                        "_ldap_attributes_": ["employeeNumber", "givenName", "sn"],
                        "uuid": "{{ employee_uuid }}",
                        "cpr_number": "{{ ldap.employeeNumber }}",
                        "given_name": "{{ ldap.givenName }}",
                        "surname": "{{ ldap.sn }}",
                    }
                }
            }
        ),
    }
)
async def test_ldap2mo_template_all_create(
    test_client: AsyncClient,
    ldap_person_dn: DN,
    ldap_person_uuid: LDAPUUID,
) -> None:
    response = await test_client.get("/Inspect/ldap2mo/all")
    assert response.status_code == 200
    result = response.json()
    assert result == "OK"

    file_data = read_jsonl_file("/tmp/ldap2mo.jsonl")
    assert file_data == [
        {
            "__ldap_uuid": str(ldap_person_uuid),
            "dn": ldap_person_dn,
            "message": "Would have uploaded changes to MO",
            "verb": "Verb.CREATE",
            "obj": {
                "uuid": ANY,
                "user_key": ANY,
                "given_name": "Aage",
                "surname": "Bach Klarskov",
                "cpr_number": "2108613133",
                "seniority": None,
                "nickname_given_name": "",
                "nickname_surname": "",
            },
        }
    ]


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
                        "_ldap_attributes_": ["employeeNumber", "givenName", "sn"],
                        "uuid": "{{ employee_uuid }}",
                        "cpr_number": "{{ ldap.employeeNumber }}",
                        "given_name": "{{ ldap.givenName }}",
                        "surname": "{{ ldap.sn }}",
                        "nickname_given_name": "Secret",
                        "nickname_surname": "Agent",
                    }
                }
            }
        ),
    }
)
async def test_ldap2mo_template_all_edit(
    test_client: AsyncClient,
    ldap_person_dn: DN,
    ldap_person_uuid: LDAPUUID,
    mo_person: UUID,
) -> None:
    response = await test_client.get("/Inspect/ldap2mo/all")
    assert response.status_code == 200
    result = response.json()
    assert result == "OK"

    file_data = read_jsonl_file("/tmp/ldap2mo.jsonl")
    assert file_data == [
        {
            "__ldap_uuid": str(ldap_person_uuid),
            "dn": ldap_person_dn,
            "message": "Would have uploaded changes to MO",
            "verb": "Verb.EDIT",
            "obj": {
                "uuid": str(mo_person),
                "user_key": str(mo_person),
                "given_name": "Aage",
                "surname": "Bach Klarskov",
                "cpr_number": "2108613133",
                "seniority": None,
                "nickname_given_name": "Secret",
                "nickname_surname": "Agent",
            },
        }
    ]


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
                        "_ldap_attributes_": ["employeeNumber", "givenName", "sn"],
                        "uuid": "{{ employee_uuid }}",
                        "cpr_number": "{{ ldap.employeeNumber }}",
                        "given_name": "{{ ldap.givenName }}",
                        "surname": "{{ ldap.sn }}",
                    }
                }
            }
        ),
    }
)
@pytest.mark.usefixtures("mo_person")
async def test_ldap2mo_template_all_no_changes(
    test_client: AsyncClient,
    ldap_person_uuid: LDAPUUID,
) -> None:
    response = await test_client.get("/Inspect/ldap2mo/all")
    assert response.status_code == 200
    result = response.json()
    assert result == "OK"

    file_data = read_jsonl_file("/tmp/ldap2mo.jsonl")
    assert file_data == [
        {
            "__ldap_uuid": str(ldap_person_uuid),
            "message": "No changes",
        }
    ]


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "CONVERSION_MAPPING": json.dumps({}),
    }
)
async def test_ldap2mo_template_all_no_config(
    test_client: AsyncClient, ldap_person_uuid: LDAPUUID
) -> None:
    response = await test_client.get("/Inspect/ldap2mo/all")
    assert response.status_code == 200
    result = response.json()
    assert result == "OK"

    file_data = read_jsonl_file("/tmp/ldap2mo.jsonl")
    assert file_data == [
        {
            "__ldap_uuid": str(ldap_person_uuid),
            "message": "No changes",
        }
    ]


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "CONVERSION_MAPPING": json.dumps({"ldap_to_mo": {}}),
    }
)
async def test_ldap2mo_template_all_empty_config(
    test_client: AsyncClient, ldap_person_uuid: LDAPUUID
) -> None:
    response = await test_client.get("/Inspect/ldap2mo/all")
    assert response.status_code == 200
    result = response.json()
    assert result == "OK"

    file_data = read_jsonl_file("/tmp/ldap2mo.jsonl")
    assert file_data == [
        {
            "__ldap_uuid": str(ldap_person_uuid),
            "message": "No changes",
        }
    ]


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
async def test_ldap2mo_template_all_skip_config(
    test_client: AsyncClient, ldap_person_uuid: LDAPUUID
) -> None:
    response = await test_client.get("/Inspect/ldap2mo/all")
    assert response.status_code == 200
    result = response.json()
    assert result == "OK"

    file_data = read_jsonl_file("/tmp/ldap2mo.jsonl")
    assert file_data == [
        {
            "__ldap_uuid": str(ldap_person_uuid),
            "message": "No changes",
        }
    ]


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
                        "_ldap_attributes_": ["employeeNumber", "givenName", "sn"],
                        "uuid": "{{ employee_uuid }}",
                        "cpr_number": "{{ ldap.employeeNumber }}",
                        "given_name": "{{ ldap.givenName }}",
                        "surname": "{{ ldap.sn }}",
                    }
                }
            }
        ),
    }
)
async def test_ldap2mo_template_all_multiple_lines(
    test_client: AsyncClient,
    add_ldap_person: AddLdapPerson,
) -> None:
    await add_ldap_person("ava", "0101700000")
    await add_ldap_person("cleo", "0101700001")
    await add_ldap_person("emily", "0101700002")

    response = await test_client.get("/Inspect/ldap2mo/all")
    assert response.status_code == 200
    result = response.json()
    assert result == "OK"

    file_data = read_jsonl_file("/tmp/ldap2mo.jsonl")
    assert len(file_data) == 3


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
                        "_ldap_attributes_": ["employeeNumber", "givenName", "sn"],
                        "uuid": "{{ employee_uuid }}",
                        "cpr_number": "{{ ldap.employeeNumber }}",
                        "given_name": "{{ ldap.givenName }}",
                        "surname": "{{ ldap.sn }}",
                    }
                }
            }
        ),
    }
)
async def test_ldap_template_start_at(
    test_client: AsyncClient,
    add_ldap_person: AddLdapPerson,
    dn2uuid: DN2UUID,
) -> None:
    async def add_ldap_person_uuid(uid: str, cpr_number: str) -> LDAPUUID:
        dn = combine_dn_strings(await add_ldap_person(uid, cpr_number))
        return await dn2uuid(dn)

    person1_uuid = await add_ldap_person_uuid("ava", "0101700000")
    person2_uuid = await add_ldap_person_uuid("cleo", "0101700001")
    person3_uuid = await add_ldap_person_uuid("emily", "0101700002")

    person_order = sorted([person1_uuid, person2_uuid, person3_uuid])

    for idx, uuid in enumerate(person_order, start=1):
        response = await test_client.get(
            "/Inspect/ldap2mo/all", params={"start_at": str(uuid)}
        )
        assert response.status_code == 200
        result = response.json()
        assert result == "OK"

        file_data = read_jsonl_file("/tmp/ldap2mo.jsonl")
        assert len(file_data) == 3 - idx
