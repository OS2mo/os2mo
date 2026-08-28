# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The built-in policies grant exactly what RBAC_MAP, PUBLIC_FIELDS and the
owner mutators grant today."""

from mora.graphapi import policies_builtin as pb
from mora.graphapi.owner_entities import OWNER_ENTITIES
from mora.graphapi.policy import Selector
from mora.graphapi.policy import SelectorKind
from mora.graphapi.rbac_map import PUBLIC_FIELDS
from mora.graphapi.rbac_map import RBAC_MAP


def _grants_for(roles: set[str]) -> set[tuple[str, str]]:
    """The (type, field) and (Mutation, name) grants the policies yield."""
    grants = set()
    for policy in pb.POLICIES:
        if not policy.applies_to(roles):
            continue
        for rule in policy.readers:
            type_name = pb.COLLECTION_TYPE[rule.collection]
            grants |= {(type_name, f) for f in rule.fields}
        grants |= policy.types.grants
        grants |= {("Mutation", m.name) for m in policy.mutators}
    return grants


def _expected(roles: set[str]) -> set[tuple[str, str]]:
    """The grants today: the public fields plus each role's RBAC_MAP fields."""
    grants = set(PUBLIC_FIELDS)
    grants |= {field for field, role in RBAC_MAP.items() if role in roles}
    return grants


def test_policies_match_rbac_map() -> None:
    """The policies are equivalent to RBAC_MAP and PUBLIC_FIELDS."""
    for roles in (set(), {"reader"}, {"admin"}, {"reader", "admin"}):
        assert _grants_for(roles) == _expected(roles)


def test_owner_mutators_match_owner_entities() -> None:
    """The owner policy's mutators are exactly the owner-checked mutators."""
    assert {m.name for m in pb.OWNER.mutators} == set(OWNER_ENTITIES)


def test_selector_matching() -> None:
    """A selector matches by kind: all always, role on membership."""
    assert Selector(SelectorKind.ALL).matches(set())
    assert Selector(SelectorKind.ROLE, "reader").matches({"reader"})
    assert not Selector(SelectorKind.ROLE, "reader").matches({"admin"})
