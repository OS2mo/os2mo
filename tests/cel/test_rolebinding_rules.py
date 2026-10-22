# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import uuid4

import pytest

from mora.cel import CelError
from mora.cel.rolebinding_rules import validate


@pytest.mark.parametrize(
    "expression",
    [
        f'ituser.uuid == "{uuid4()}"',
        'ituser.user_key == "bob"',
        'ituser.external_id == "S-1-5-21"',
        f'ituser.engagements.exists(e, e.uuid == "{uuid4()}")',
        f'ituser.engagements.exists(e, e.engagement_type.uuid == "{uuid4()}")',
        f'ituser.engagements.exists(e, e.job_function.uuid == "{uuid4()}")',
        f'ituser.engagements.exists(e, "{uuid4()}" in e.org_unit.path_uuids)',
        f'ituser.engagements.all(e, e.org_unit.uuid == "{uuid4()}")',
        f'ituser.engagements.exists(e, e.job_function.uuid in ["{uuid4()}", "{uuid4()}"])',
        f'ituser.uuid.startsWith("{str(uuid4())[:8]}")',
        "ituser.engagements.exists(e, size(e.org_unit.path_uuids) > 1)",
        "size(ituser.engagements) == 0",
    ],
)
def test_accepted(expression: str) -> None:
    validate(expression)


@pytest.mark.parametrize(
    "expression,message",
    [
        ("", "empty"),
        ("ituser.uuid ==", "Syntax error"),
        ("nosuchfunction(ituser)", "undeclared reference"),
        ('employee.uuid == "x"', "undeclared reference"),
        (
            "has(ituser.engagment)",
            "undefined field 'engagment' not found in struct 'mo.rolebinding.ITUser'",
        ),
        (
            'ituser.engagements.job_function.uuid == "x"',
            "cannot be the operand of a select operation",
        ),
        ("ituser.uuid", "must be true or false, but is STRING"),
        (
            "ituser.engagements",
            "must be true or false, but is LIST<mo.rolebinding.Engagement>",
        ),
        ("42", "must be true or false, but is INT"),
    ],
)
def test_rejected(expression: str, message: str) -> None:
    with pytest.raises(CelError, match=message):
        validate(expression)
