# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Evaluation of the built-in policies against a field or mutator access.

The evaluator is given the caller's roles and the field being resolved, and
returns whether any applicable policy grants the access. Read rules and type
rules grant `(type, field)` pairs; mutators grant `(Mutation, name)`. The owner
policy's mutators additionally require the owner check against the database.
"""

from mora.graphapi import policies_builtin as builtin
from mora.graphapi.policy import Policy


def _applicable_policies(roles: set[str]) -> list[Policy]:
    """The active policies selecting a principal holding `roles`."""
    return [policy for policy in builtin.POLICIES if policy.applies_to(roles)]


def field_grants(roles: set[str]) -> set[tuple[str, str]]:
    """The `(type, field)` pairs the applicable policies grant for reading."""
    grants: set[tuple[str, str]] = set()
    for policy in _applicable_policies(roles):
        for rule in policy.readers:
            type_name = builtin.COLLECTION_TYPE[rule.collection]
            grants |= {(type_name, field) for field in rule.fields}
        grants |= policy.types.grants
    return grants


def mutator_names(roles: set[str]) -> set[str]:
    """The mutator names the applicable policies grant outright.

    The owner policy's mutators are excluded: they are subject to the owner
    check, run separately by `owner_policy` against the call arguments.
    """
    return {
        mutator.name
        for policy in _applicable_policies(roles)
        for mutator in policy.mutators
        if policy is not builtin.OWNER
    }
