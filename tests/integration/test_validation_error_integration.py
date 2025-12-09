# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json
from uuid import uuid4

import pytest
from fastramqpi.context import Context
from pydantic import ValidationError

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
                        "_ldap_attributes_": ["employeeID"],
                        "cpr_number": "{{ldap.employeeID or None}}",
                        "uuid": "{{ employee_uuid or '' }}",
                    },
                    "Custom": {
                        "objectClass": "Custom.JobTitleFromADToMO",
                        "_import_to_mo_": "true",
                        "_ldap_attributes_": ["hkStsuuid"],
                        "user": "{{ ldap.hkStsuuid }}",
                        "job_function": f"{{ {uuid4()} }}",  # Invalid UUID format
                        "uuid": "{{ employee_uuid or '' }}",
                    },
                }
            }
        ),
    }
)
@pytest.mark.integration_test
async def test_ldap_to_mo_dict_validation_error(context: Context) -> None:
    """Test for ValidationError when a Jinja template produces invalid data."""
    user_context = context["user_context"]
    settings = user_context["settings"]
    converter = user_context["converter"]

    with pytest.raises(ValidationError) as exc_info:
        assert settings.conversion_mapping.ldap_to_mo is not None
        await converter.from_ldap(
            LdapObject(
                dn="",
                hkStsuuid="not_an_uuid",
                title="job title",
                comment="job title default",
            ),
            mapping=settings.conversion_mapping.ldap_to_mo["Custom"],
            template_context={
                "employee_uuid": str(uuid4()),
            },
        )
    assert "2 validation errors for JobTitleFromADToMO" in str(exc_info.value)
    assert "value is not a valid uuid" in str(exc_info.value)
