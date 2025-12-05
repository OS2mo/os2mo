# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json
from uuid import UUID

import pytest
from fastapi.encoders import jsonable_encoder
from fastramqpi.events import Event
from httpx import AsyncClient

from mo_ldap_import_export.exceptions import NoObjectsReturnedException
from mo_ldap_import_export.ldapapi import LDAPAPI

DRY_RUN_CONVERSION_MAPPING = {
    "mo_to_ldap": [
        {
            "identifier": "person",
            "routing_key": "person",
            "object_class": "inetOrgPerson",
            "template": """
                {% set mo_employee = load_mo_employee(uuid) %}
                {{
                    {
                        "dn": "cn=" + mo_employee.given_name + " " + mo_employee.surname + ",ou=os2mo,o=magenta,dc=magenta,dc=dk",
                        "create": True,
                        "attributes": {
                            "employeeNumber": mo_employee.cpr_number,
                            "sn": mo_employee.surname
                        }
                    }|tojson
                }}
            """,
        }
    ]
}

EXPECTED_DN = "cn=Aage Bach Klarskov,ou=os2mo,o=magenta,dc=magenta,dc=dk"


@pytest.mark.integration_test
@pytest.mark.usefixtures("ldap_org_unit")
@pytest.mark.envvar({"CONVERSION_MAPPING": json.dumps(DRY_RUN_CONVERSION_MAPPING)})
async def test_mo_to_ldap_dry_run_true(
    test_client: AsyncClient,
    ldap_api: LDAPAPI,
    mo_person: UUID,
) -> None:
    # Call the MO --> LDAP synchronization logic with dry-run = True
    response = await test_client.post(
        "/mo_to_ldap/person",
        params={"dry_run": True},
        json=jsonable_encoder(Event(subject=mo_person, priority=10)),
    )
    assert response.status_code == 451
    response_json = response.json()
    assert response_json["detail"]["message"] == "Would have created"
    dn = response_json["detail"]["dn"]
    assert dn == EXPECTED_DN

    # Ensure that no LDAP account was created
    with pytest.raises(NoObjectsReturnedException):
        await ldap_api.get_object_by_dn(dn)


@pytest.mark.integration_test
@pytest.mark.usefixtures("ldap_org_unit")
@pytest.mark.envvar({"CONVERSION_MAPPING": json.dumps(DRY_RUN_CONVERSION_MAPPING)})
@pytest.mark.parametrize("dry_run", [False, None])
async def test_mo_to_ldap_no_dry_run(
    test_client: AsyncClient,
    ldap_api: LDAPAPI,
    mo_person: UUID,
    dry_run: bool | None,
) -> None:
    # Call the MO --> LDAP synchronization logic
    response = await test_client.post(
        "/mo_to_ldap/person",
        params={"dry_run": True} if dry_run else {},
        json=jsonable_encoder(Event(subject=mo_person, priority=10)),
    )
    assert response.status_code == 200

    # Ensure that an LDAP account was created
    ldap_object = await ldap_api.get_object_by_dn(EXPECTED_DN)
    assert ldap_object is not None
