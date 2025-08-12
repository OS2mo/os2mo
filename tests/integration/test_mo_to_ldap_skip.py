# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json
from collections.abc import Awaitable
from collections.abc import Callable
from uuid import UUID
from uuid import uuid4

import pytest
from structlog.testing import capture_logs


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
        "LDAP_CPR_ATTRIBUTE": "employeeNumber",
        "CONVERSION_MAPPING": json.dumps(
            {
                "mo_to_ldap": [
                    {
                        "identifier": "person2skip",
                        "routing_key": "person",
                        "object_class": "inetOrgPerson",
                        "template": """
                        {{ skip_if_none(None) }}
                    """,
                    },
                ],
            }
        ),
    }
)
@pytest.mark.usefixtures("ldap_org_unit")
async def test_rolebinding_sync(
    trigger_mo_to_ldap_sync: Callable[[str, UUID], Awaitable[None]],
) -> None:
    with capture_logs() as cap_logs:
        await trigger_mo_to_ldap_sync("person2skip", uuid4())

    assert cap_logs == [
        {
            "event": "Registered change in handler",
            "log_level": "info",
        },
        {
            "event": "Skipping object as requested",
            "log_level": "info",
        },
    ]
