# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The CEL environment rules are written against."""

import pytest

from mora.rolebinding_rules.cel import CelError
from mora.rolebinding_rules.cel import compile

NURSE = "8d3b34c1-1e2f-4a05-8a1f-58b1d2f0e3aa"
DOCTOR = "1b0d9f2e-5c3a-4f18-9a77-0b2c4d6e8f10"
UNIT = "2f1a63a2-2d47-4a2f-b7c9-4a0e1ba0c1de"
PERSON = "0fb62199-cb9e-4083-ba45-2a63bfd142d7"


@pytest.mark.parametrize(
    "expression",
    [
        f'ituser.person.uuid == "{PERSON}"',
        f'ituser.engagement.job_function.uuid == "{NURSE}"',
        f'"{UNIT}" in ituser.engagement.org_unit.path_uuids',
        "ituser.engagement == null",
        f'ituser.engagement.job_function.uuid in ["{NURSE}", "{DOCTOR}"]',
        f'ituser.person.uuid.startsWith("{PERSON[:8]}")',
        "size(ituser.engagement.org_unit.path_uuids) > 1",
        f'ituser.engagement != null ? ituser.engagement.org_unit.uuid == "{UNIT}" : false',
        "has(ituser.engagement)",
    ],
)
def test_accepted(expression: str) -> None:
    compile(expression)


@pytest.mark.parametrize(
    "expression,message",
    [
        ("", "empty"),
        ("ituser.person.uuid ==", "Syntax error"),
        ("nosuchfunction(ituser)", "undeclared reference"),
        ('employee.uuid == "x"', "undeclared reference"),
        ("ituser.person.uuid", "must be true or false"),
        ("42", "must be true or false"),
    ],
)
def test_rejected(expression: str, message: str) -> None:
    with pytest.raises(CelError, match=message):
        compile(expression)
