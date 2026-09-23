# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Testing the evaluation of CEL conditions."""

from datetime import datetime
from typing import Any

import pytest

from mora.auth.keycloak.models import RealmAccess
from mora.auth.keycloak.models import Token
from mora.graphapi.policy_cel import evaluate
from tests.conftest import ALVIDA_UUID
from tests.conftest import BRUCE_UUID


@pytest.mark.parametrize(
    "condition,expected",
    [
        (
            '{"uuids": [token.uuid]}',
            {"uuids": [str(BRUCE_UUID)]},
        ),
        (
            '{"employee": {"uuids": [token.uuid]}}',
            {"employee": {"uuids": [str(BRUCE_UUID)]}},
        ),
        (
            f'token.uuid == "{BRUCE_UUID}" ? {{"user_keys": ["email"]}} : {{}}',
            {"user_keys": ["email"]},
        ),
        (
            f'token.uuid != "{BRUCE_UUID}" ? {{"user_keys": ["email"]}} : {{}}',
            {},
        ),
    ],
)
async def test_a_condition_yields_the_filter_it_names(
    condition: str, expected: dict
) -> None:
    """A condition is evaluated on the caller's token, down to plain values."""
    token = Token(azp="mo", uuid=BRUCE_UUID, realm_access=RealmAccess(roles={"reader"}))

    assert evaluate(condition, token, {}) == expected


@pytest.mark.parametrize(
    "condition,expected",
    [
        ('{"uuids": [args.input.org_unit]}', {"uuids": [str(ALVIDA_UUID)]}),
        ("args.input.org_unit != null", True),
        # A field the input carries as null is there to ask about
        ("args.input.person != null", False),
        ("has(args.input.person)", True),
        # A field the arguments do not carry at all is absent
        ("has(args.input.engagement)", False),
        ("args.input.validity.from", "2000-01-01T00:00:00"),
    ],
)
async def test_a_condition_yields_what_the_arguments_name(
    condition: str, expected: Any
) -> None:
    """A condition is evaluated on the arguments, down to plain values."""
    token = Token(azp="mo", uuid=BRUCE_UUID, realm_access=RealmAccess(roles={"owner"}))
    args = {
        "input": {
            "org_unit": ALVIDA_UUID,
            "person": None,
            "validity": {"from": datetime(2000, 1, 1)},
        }
    }

    assert evaluate(condition, token, args) == expected


async def test_a_condition_names_a_value_once_with_bind() -> None:
    """A condition binds a value to a name with `cel.bind`."""
    token = Token(azp="mo", uuid=BRUCE_UUID, realm_access=RealmAccess(roles={"owner"}))

    assert evaluate("cel.bind(me, token.uuid, [me, me])", token, {}) == [
        str(BRUCE_UUID),
        str(BRUCE_UUID),
    ]


async def test_a_condition_reaching_for_what_the_token_lacks_fails() -> None:
    """A condition naming something the context has not is an error, not a denial."""
    token = Token(azp="mo", uuid=BRUCE_UUID, realm_access=RealmAccess(roles={"reader"}))

    with pytest.raises(ValueError) as raised:
        evaluate("token.nonsense.deeper", token, {})

    assert str(raised.value) == (
        "condition 'token.nonsense.deeper' failed: "
        'NOT_FOUND: Key not found in map : "nonsense"'
    )
