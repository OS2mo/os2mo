# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json
from uuid import uuid4

import pytest
from fastramqpi.context import Context

from mo_ldap_import_export.exceptions import IncorrectMapping
from mo_ldap_import_export.ldap_classes import LdapObject


@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
        "CONVERSION_MAPPING": json.dumps(
            {
                "ldap_to_mo": {
                    "Active Directory": {
                        "objectClass": "ITUser",
                        "_import_to_mo_": "True",
                        "_ldap_attributes_": ["msSFU30Name"],
                        "user_key": "{{ ldap.msSFU30Name or '' }}",
                        "itsystem": "{ 'hep': 'hey }",  # Malformed JSON
                        "person": "{{ dict(uuid=employee_uuid or '') }}",
                    }
                },
            }
        ),
    }
)
@pytest.mark.integration_test
async def test_ldap_to_mo_dict_error(context: Context) -> None:
    """Test for IncorrectMapping when a Jinja template produces malformed JSON."""
    user_context = context["user_context"]
    settings = user_context["settings"]
    converter = user_context["converter"]

    with pytest.raises(IncorrectMapping) as exc_info:
        assert settings.conversion_mapping.ldap_to_mo is not None
        await converter.from_ldap(
            LdapObject(
                dn="",
                msSFU30Name=["bar"],
                itSystemName=["Active Directory"],
            ),
            mapping=settings.conversion_mapping.ldap_to_mo["Active Directory"],
            template_context={
                "employee_uuid": str(uuid4()),
            },
        )
        assert "Could not convert { 'hep': 'hey } in 'itsystem' to dict" in str(
            exc_info.value
        )
        assert (
            "context={'ldap': {'dn': '', 'itSystemName': 'Active Directory', 'msSFU30Name': 'bar'}"
            in str(exc_info.value)
        )
