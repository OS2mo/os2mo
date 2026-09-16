# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests of the CEL expressions a policy rule carries."""

from typing import Any
from uuid import uuid4

import pytest

from mora.auth.keycloak.models import Token
from mora.config import Settings
from mora.graphapi.policy_cel import build_activation
from mora.graphapi.policy_cel import check_condition
from mora.graphapi.policy_cel import evaluate_filter

ALICE = uuid4()
UNIT = uuid4()


@pytest.fixture
def activation():
    token = Token(
        azp="vue",
        preferred_username="alice",
        realm_access={"roles": {"reader"}},
        uuid=str(ALICE),
    )
    args: dict[str, Any] = {"input": {"org_unit": UNIT, "person": None}}
    return build_activation(token, Settings(), args)


def test_a_rule_without_a_condition_applies(activation) -> None:
    assert check_condition("", activation) is True


def test_a_condition_reads_the_caller(activation) -> None:
    assert check_condition('"reader" in token.roles', activation) is True
    assert check_condition('"owner" in token.roles', activation) is False
    assert check_condition('token.preferred_username == "alice"', activation) is True


def test_a_condition_must_be_boolean(activation) -> None:
    with pytest.raises(ValueError, match="result is not boolean"):
        check_condition('"a string"', activation)


def test_a_filter_yields_the_graphql_filter(activation) -> None:
    assert evaluate_filter('{"uuids": [token.uuid]}', activation) == {
        "uuids": [str(ALICE)]
    }


def test_a_filter_reads_the_call_arguments(activation) -> None:
    """The arguments of the call are plain data, whatever the scalars coerced."""
    assert evaluate_filter("[args.input.org_unit]", activation) == [str(UNIT)]
    assert (
        evaluate_filter(
            "has(args.input.person) && args.input.person != null", activation
        )
        is False
    )


def test_a_filter_surfaces_its_errors(activation) -> None:
    with pytest.raises(ValueError, match="failed to evaluate CEL filter"):
        evaluate_filter("token.misspelt.field", activation)
