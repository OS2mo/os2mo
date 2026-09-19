# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Testing the evaluation of CEL conditions."""

import pytest

from mora.auth.keycloak.models import RealmAccess
from mora.auth.keycloak.models import Token
from mora.graphapi.policy_cel import evaluate
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
            '"reader" in token.roles ? {"user_keys": ["email"]} : {}',
            {"user_keys": ["email"]},
        ),
        (
            '"owner" in token.roles ? {"user_keys": ["email"]} : {}',
            {},
        ),
    ],
)
async def test_a_condition_yields_the_filter_it_names(
    condition: str, expected: dict
) -> None:
    """A condition is evaluated on the caller's token, down to plain values."""
    token = Token(azp="mo", uuid=BRUCE_UUID, realm_access=RealmAccess(roles={"reader"}))

    assert evaluate(condition, token) == expected


async def test_a_condition_reaching_for_what_the_token_lacks_fails() -> None:
    """A condition naming something the context has not is an error, not a denial."""
    token = Token(azp="mo", uuid=BRUCE_UUID, realm_access=RealmAccess(roles={"reader"}))

    with pytest.raises(ValueError) as raised:
        evaluate("token.nonsense.deeper", token)

    assert str(raised.value) == (
        "condition 'token.nonsense.deeper' failed: "
        'NOT_FOUND: Key not found in map : "nonsense"'
    )
