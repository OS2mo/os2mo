# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests of the CEL evaluation helpers for policy conditions and filters."""

from types import SimpleNamespace
from uuid import uuid4

import pytest

from mora.graphapi.policy_cel import build_activation
from mora.graphapi.policy_cel import check_condition
from mora.graphapi.policy_cel import evaluate_condition
from mora.graphapi.policy_cel import evaluate_filter


def _token(**overrides):
    return SimpleNamespace(
        uuid=uuid4(),
        preferred_username="alice",
        realm_access=SimpleNamespace(roles={"reader", "admin"}),
        **overrides,
    )


def test_check_condition_empty_is_true() -> None:
    """A rule without a condition always applies."""
    assert check_condition("", build_activation(_token(), {})) is True


def test_check_condition_delegates() -> None:
    """A rule with a condition is checked by evaluating it."""
    activation = build_activation(_token(), {})
    assert check_condition("true", activation) is True
    assert check_condition("false", activation) is False


def test_condition_reads_token_and_args() -> None:
    """A condition may read the token and the call arguments."""
    activation = build_activation(_token(), {"uuid": "1234"})
    assert evaluate_condition('"reader" in token.roles', activation) is True
    assert evaluate_condition('"owner" in token.roles', activation) is False
    assert evaluate_condition('args.uuid == "1234"', activation) is True


def test_condition_must_be_boolean() -> None:
    """A non-boolean condition surfaces an error."""
    with pytest.raises(ValueError, match="result is not boolean"):
        evaluate_condition('"a string"', build_activation(_token(), {}))


def test_evaluate_filter_yields_json() -> None:
    """A filter evaluates to its result as JSON."""
    activation = build_activation(_token(), {})
    assert evaluate_filter('[{"collection": "employee"}]', activation) == (
        '[{"collection": "employee"}]'
    )


def test_evaluate_filter_surfaces_errors() -> None:
    """A filter erroring in CEL surfaces the error."""
    with pytest.raises(ValueError, match="failed to evaluate CEL filter"):
        evaluate_filter("token.misspelt.field", build_activation(_token(), {}))
