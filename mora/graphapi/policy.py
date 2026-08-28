# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The policy model: a policy is a selector, read rules and mutators.

A policy `p` is a collection of three fields:

- `selector` (`s`): the principal selector, matching actors by `kind`/`value`.
- `readers` (`r`): the read rules. A read rule states that a set of fields on a
  collection may be read on objects passing a CEL condition `k`, where `k`
  yields a GraphQL filter object on the collection. An empty `k` selects every
  object of the collection.
- `mutators` (`m`): the mutators that may be executed. Each carries a CEL
  condition `mk` which, if empty, disallows the operation and, if non-empty,
  allows it. Both read rules and mutators may carry a secondary CEL expression
  for non-database lookups, i.e. checking the value of the call arguments.

This module holds the data structures only; the built-in policies and their
enforcement live elsewhere.
"""

from dataclasses import dataclass
from enum import Enum

# A CEL expression. The empty string means "no expression"
CEL = str


class SelectorKind(Enum):
    """The kind of principal attribute a selector matches on."""

    # Matches an actor based on their Keycloak roles; `value` is the role
    ROLE = "role"
    # Matches every actor; `value` is ignored
    ALL = "all"


@dataclass(frozen=True)
class Selector:
    """A principal selector: which actors the policy applies to."""

    kind: SelectorKind
    value: str = ""

    def matches(self, roles: set[str]) -> bool:
        """Whether a principal holding `roles` is selected."""
        match self.kind:
            case SelectorKind.ALL:
                return True
            case SelectorKind.ROLE:
                return self.value in roles


@dataclass(frozen=True)
class ReadRule:
    """Fields readable on a collection's objects passing condition `k`.

    `collection` names the collection whose objects the rule reads; `fields`
    the readable fields on the collection's type. `k` is a CEL expression
    yielding a GraphQL filter on the collection, selecting the objects the rule
    reaches; an empty `k` selects every object. `condition` is a secondary CEL
    expression for non-database lookups, e.g. checking the call arguments; an
    empty `condition` always holds.
    """

    collection: str
    fields: frozenset[str] = frozenset()
    k: CEL = ""
    condition: CEL = ""


@dataclass(frozen=True)
class TypeRule:
    """Fields readable on named GraphQL types, independent of any collection.

    Used for the structural types a collection's objects are reached through:
    the paged/response/registration wrappers, scalar value types and the
    top-level query fields. `grants` are `(type, field)` pairs.
    """

    grants: frozenset[tuple[str, str]] = frozenset()


@dataclass(frozen=True)
class Mutator:
    """A mutator that may be executed, gated by conditions.

    `name` is the GraphQL mutation field. `mk` is a CEL condition which, if
    empty, disallows the operation and, if non-empty, allows it. `k` is a CEL
    expression yielding the entity check-specs the mutator touches, verified
    against the database; an empty `k` checks nothing.
    """

    name: str
    mk: CEL = ""
    k: CEL = ""


@dataclass(frozen=True)
class Policy:
    """A named policy: a selector, its read rules and its mutators."""

    name: str
    selector: Selector
    readers: tuple[ReadRule, ...] = ()
    mutators: tuple[Mutator, ...] = ()
    types: TypeRule = TypeRule()
    # Whether the policy is in effect; a policy only grants access while active
    active: bool = True

    def applies_to(self, roles: set[str]) -> bool:
        """Whether this policy is active and selects a principal with `roles`."""
        return self.active and self.selector.matches(roles)
