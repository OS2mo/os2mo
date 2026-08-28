# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests of the policy base-predicate evaluation."""

import pytest

from mora.graphapi import policy_eval
from mora.graphapi.policy import ReadRule


def test_predicate_no_rules_is_false() -> None:
    """A caller holding no read rule on a collection sees none of it."""
    assert str(policy_eval._predicate_from_rules(None, "employee", [])) == "false"


def test_predicate_empty_k_restricts_nothing() -> None:
    """A read rule with an empty k selects the whole collection."""
    rules = [ReadRule(collection="employee")]
    assert str(policy_eval._predicate_from_rules(None, "employee", rules)) == "true"


def test_predicate_filtered_rules_not_yet_evaluated() -> None:
    """A read rule carrying a filter is not yet evaluated."""
    rules = [ReadRule(collection="employee", k='[{"collection": "employee"}]')]
    with pytest.raises(NotImplementedError, match="not yet evaluated"):
        policy_eval._predicate_from_rules(None, "employee", rules)


def test_mutator_names_excludes_owner() -> None:
    """The outright mutator names exclude the owner policy's, which are gated."""
    assert "employee_update" not in policy_eval.mutator_names(set())
    assert "employee_update" in policy_eval.mutator_names({"admin"})
