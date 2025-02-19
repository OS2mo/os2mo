# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json
from collections.abc import Awaitable
from collections.abc import Callable

import pytest
from structlog.testing import capture_logs


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
        "CONVERSION_MAPPING": json.dumps(
            {
                "mo2ldap": """
                    {% set mo_employee = load_mo_employee(uuid, current_objects_only=False) %}
                    {{
                        {
                            "employeeNumber": mo_employee.cpr_number,
                            "carLicense": mo_employee.uuid|string,
                            "cn": mo_employee.given_name + " " + mo_employee.surname,
                            "sn": mo_employee.surname,
                            "givenName": mo_employee.given_name,
                            "displayName": mo_employee.nickname_given_name + " " + mo_employee.nickname_surname
                        }|tojson
                    }}
                """,
                "username_generator": {
                    "objectClass": "UserNameGenerator",
                    "combinations_to_try": ["FFFX", "LLLX"],
                },
            }
        ),
    }
)
@pytest.mark.usefixtures("ldap_person")
async def test_no_log_spam(
    trigger_mo_person: Callable[[], Awaitable[None]],
) -> None:
    # Forcefully synchronizing changes data the first time
    with capture_logs() as cap_logs:
        await trigger_mo_person()
    events = [m["event"] for m in cap_logs]
    assert "Not writing to LDAP as changeset is empty" not in events
    assert "Uploading object" in events

    # Forcefully synchronizing again does not change data
    with capture_logs() as cap_logs:
        await trigger_mo_person()
    events = [m["event"] for m in cap_logs]
    assert "Not writing to LDAP as changeset is empty" in events
    assert "Uploading object" not in events
