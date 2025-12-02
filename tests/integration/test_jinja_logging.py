# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

import pytest
from structlog.testing import capture_logs

from mo_ldap_import_export.ldap import evaluate_template
from mo_ldap_import_export.types import DN


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "log_level,template_string",
    [
        ("info", "{{ logger.info('hello from jinja') }}"),
        ("warning", "{{ logger.warning('hello from jinja') }}"),
        ("error", "{{ logger.error('hello from jinja') }}"),
    ],
)
async def test_log_from_jinja(log_level: str, template_string: str) -> None:
    with capture_logs() as logs:
        template_result = await evaluate_template(
            template_string, dn=DN("o=test"), mapping={}
        )

    assert template_result is False
    assert logs == [
        {
            "log_level": log_level,
            "event": "hello from jinja",
        }
    ]
