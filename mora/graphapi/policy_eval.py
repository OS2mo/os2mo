# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Evaluation of the built-in policies against a field or mutator access.

The evaluator is given the caller's roles and the field being resolved, and
returns whether any applicable policy grants the access. Read rules and type
rules grant `(type, field)` pairs; mutators grant `(Mutation, name)`. The owner
policy's mutators additionally require the owner check against the database.
"""

from typing import TYPE_CHECKING

from sqlalchemy import ColumnElement
from sqlalchemy import false
from sqlalchemy import true

if TYPE_CHECKING:
    from mora.graphapi.context import MOContext
    from mora.graphapi.context import MOInfo

from mora.graphapi import policies_builtin as builtin
from mora.graphapi.permissions import Collections
from mora.graphapi.policy import Policy
from mora.graphapi.policy import ReadRule


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


def _read_rules_for(roles: set[str], collection: Collections) -> list[ReadRule]:
    """The applicable read rules naming `collection`."""
    return [
        rule
        for policy in _applicable_policies(roles)
        for rule in policy.readers
        if rule.collection == collection
    ]


def _predicate_from_rules(
    info: "MOInfo | None",
    collection: Collections,
    rules: list[ReadRule],
) -> ColumnElement:
    """The predicate the read `rules` allow on `collection`.

    It is the OR of the rules' filters: a rule with an empty `k` selects every
    object, so the caller sees the whole collection. A caller holding no read
    rule on the collection sees none of it. CEL `k` filters are not yet
    evaluated; every built-in rule has an empty `k`, so this is permissive.
    """
    if not rules:
        # No read rule on the collection: nothing of it is visible
        return false()
    # A rule with an empty k selects every object, so it restricts nothing.
    # Every built-in rule has an empty k, so the base is permissive. A rule
    # carrying a filter would contribute only its k, evaluated as a predicate
    # on the collection; none exist yet among the built-ins.
    if any(not rule.k for rule in rules):
        return true()
    raise NotImplementedError("CEL k filters are not yet evaluated")


async def _base_rules(context: "MOContext", collection: Collections) -> list[ReadRule]:
    """The caller's read rules for `collection`, fetched once per request."""
    cache = context.base_predicates
    if collection not in cache:
        token = await context.get_token()
        roles = set(token.realm_access.roles)
        cache[collection] = _read_rules_for(roles, collection)
    return cache[collection]


async def base_predicate_for(info: "MOInfo", collection: Collections) -> ColumnElement:
    """The collection's base predicate for this request.

    The caller's read rules are cached per request. Nested reads (whose parent
    is not the query root) are not restricted: they follow the object they hang
    off.
    """
    if info._raw_info.parent_type.name != "Query":
        return true()
    rules = await _base_rules(info.context, collection)
    return _predicate_from_rules(info, collection, rules)
