# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Evaluation of the policies against a field or mutator access.

The policies are loaded from the database at startup; until then the hardcoded
built-ins, which the seeded rows mirror, are enforced. The evaluator is given
the caller's roles and the field being resolved, and returns whether any
applicable policy grants the access. Read rules and type rules grant
`(type, field)` pairs; mutators grant `(Mutation, name)`. The owner policy's
mutators additionally require the owner check against the database.
"""

from typing import TYPE_CHECKING

from more_itertools import one
from sqlalchemy import ColumnElement
from sqlalchemy import false
from sqlalchemy import select
from sqlalchemy import true
from sqlalchemy.orm import selectinload

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from mora.graphapi.context import MOContext
    from mora.graphapi.context import MOInfo

from mora.db import Policy as PolicyRow
from mora.graphapi import policies_builtin as builtin
from mora.graphapi.permissions import Collections
from mora.graphapi.policy import Mutator
from mora.graphapi.policy import Policy
from mora.graphapi.policy import ReadRule
from mora.graphapi.policy import Selector
from mora.graphapi.policy import SelectorKind
from mora.graphapi.policy import TypeRule

# The policies in effect, loaded from the database at startup. Until then the
# hardcoded built-ins are enforced, which the seeded rows mirror.
_policies: tuple[Policy, ...] = builtin.POLICIES


def _to_policy(row: PolicyRow) -> Policy:
    """The in-code `Policy` a database row expresses."""
    s = one(row.selectors)
    return Policy(
        name=row.name,
        selector=Selector(kind=SelectorKind(s.kind.value), value=s.value),
        readers=tuple(
            ReadRule(
                collection=r.collection,
                fields=frozenset(r.fields),
                k=r.k,
                condition=r.condition,
            )
            for r in row.readers
        ),
        mutators=tuple(Mutator(name=m.name, mk=m.mk, k=m.k) for m in row.mutators),
        types=TypeRule(grants=frozenset((g.type, g.field) for g in row.type_grants)),
        active=row.active,
    )


async def load_policies(session: "AsyncSession") -> None:
    """Load the policies from the database into effect."""
    global _policies
    rows = (
        (
            await session.scalars(
                select(PolicyRow).options(
                    selectinload(PolicyRow.selectors),
                    selectinload(PolicyRow.readers),
                    selectinload(PolicyRow.mutators),
                    selectinload(PolicyRow.type_grants),
                )
            )
        )
        .unique()
        .all()
    )
    _policies = tuple(_to_policy(row) for row in rows)


def _applicable_policies(roles: set[str]) -> list[Policy]:
    """The active policies selecting a principal holding `roles`."""
    return [policy for policy in _policies if policy.applies_to(roles)]


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
