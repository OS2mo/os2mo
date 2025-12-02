# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json
from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any

import pytest
from structlog.testing import capture_logs

from mo_ldap_import_export.types import EmployeeUUID


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
        "CONVERSION_MAPPING": json.dumps(
            {
                "mo2ldap": """
                    {% set mo_employee = load_mo_employee(uuid, current_objects_only=False) %}

                    {% set employee_uuid_str = uuid|string %}
                    {% set employee_cpr = mo_employee.cpr_number %}
                    {% set employee_given_name = mo_employee.given_name %}
                    {% set employee_surname = mo_employee.surname %}
                    {% set employee_cn = employee_given_name + " " + employee_surname %}

                    {% set _ = logger.info("uuid", uuid=employee_uuid_str) %}
                    {% set _ = logger.info("cpr_number", cpr_number=employee_cpr) %}
                    {% set _ = logger.info("given_name", given_name=employee_given_name) %}
                    {% set _ = logger.info("surname", surname=employee_surname) %}
                    {{
                        {
                            "employeeNumber": employee_cpr,
                            "givenName": employee_given_name,
                            "sn": employee_surname,
                            "cn": employee_cn,
                            "carLicense": employee_uuid_str
                        }|tojson
                    }}
                """,
                "username_generator": {
                    "combinations_to_try": ["FFFX", "LLLX"],
                },
            }
        ),
    }
)
async def test_structured_logging(
    trigger_mo_person: Callable[[], Awaitable[None]],
    assert_ldap_person: Callable[[dict[str, Any]], Awaitable[None]],
    mo_person: EmployeeUUID,
) -> None:
    with capture_logs() as logs:
        await trigger_mo_person()

    # Verify that the person was created in LDAP
    await assert_ldap_person(
        {
            "uid": ["abk"],
            "cn": ["Aage Bach Klarskov"],
            "givenName": ["Aage"],
            "sn": ["Bach Klarskov"],
            "employeeNumber": "2108613133",
            "carLicense": [str(mo_person)],
            "displayName": [],
        }
    )

    # Check for the expected log messages
    log_events = ["uuid", "cpr_number", "given_name", "surname"]
    filtered_logs = [log for log in logs if log["event"] in log_events]
    assert filtered_logs == [
        {
            "event": "uuid",
            "log_level": "info",
            "uuid": str(mo_person),
        },
        {
            "cpr_number": "2108613133",
            "event": "cpr_number",
            "log_level": "info",
        },
        {
            "event": "given_name",
            "given_name": "Aage",
            "log_level": "info",
        },
        {
            "event": "surname",
            "log_level": "info",
            "surname": "Bach Klarskov",
        },
    ]
