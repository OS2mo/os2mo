# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json
from unittest.mock import ANY
from uuid import uuid4

import pytest
from fastramqpi.context import Context

from mo_ldap_import_export.ldap_classes import LdapObject


@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
        "CONVERSION_MAPPING": json.dumps(
            {
                "ldap_to_mo": {
                    "Employee": {
                        "objectClass": "Employee",
                        "_import_to_mo_": "True",
                        "_ldap_attributes_": ["givenName", "sn"],
                        "user_key": "{{ ldap.dn }}",
                        "given_name": "{{ ldap.get('givenName', 'given_name') }}",
                        "surname": "{{ ldap.sn if 'sn' in ldap else 'surname' }}",
                        "cpr_number": "{{ ldap.get('cpr') }}",
                        "uuid": "{{ employee_uuid }}",
                    }
                }
            }
        ),
    }
)
@pytest.mark.integration_test
@pytest.mark.parametrize(
    "ldap_values,expected",
    (
        # Base case
        ({}, {}),
        # Single overrides
        ({"cpr": "0101700000"}, {"cpr_number": "0101700000"}),
        ({"givenName": "Hans"}, {"given_name": "Hans"}),
        ({"sn": "Petersen"}, {"surname": "Petersen"}),
        # Empty values -> no keys
        ({"cpr": ""}, {}),
        ({"givenName": ""}, {"given_name": None}),
        ({"sn": ""}, {"surname": None}),
    ),
)
async def test_template_strictness(
    context: Context, ldap_values: dict[str, str], expected: dict[str, str]
) -> None:
    """Test various Jinja template strictness scenarios in LdapConverter."""
    user_context = context["user_context"]
    settings = user_context["settings"]
    converter = user_context["converter"]

    assert settings.conversion_mapping.ldap_to_mo is not None
    employee = await converter.from_ldap(
        LdapObject(dn="CN=foo", **ldap_values),
        mapping=settings.conversion_mapping.ldap_to_mo["Employee"],
        template_context={
            "employee_uuid": str(uuid4()),
        },
    )
    expected_employee = {
        "uuid": ANY,
        "user_key": "CN=foo",
        "given_name": "given_name",
        "surname": "surname",
    }
    for key, value in expected.items():
        if value is None:
            del expected_employee[key]
        else:
            expected_employee[key] = value

    assert employee.dict(exclude_unset=True) == expected_employee
