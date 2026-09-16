# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""What the policies of a caller grant them, as one operation sees it."""

from typing import Any
from typing import NamedTuple
from typing import TypeAlias
from uuid import UUID

from sqlalchemy import ColumnElement

# OIDC token role
Role: TypeAlias = str
# GraphQL collection
Collection: TypeAlias = str
# GraphQL field
Field: TypeAlias = str
# GraphQL mutator
Mutator: TypeAlias = str
# A CEL expression. The empty string means "no expression"
CEL: TypeAlias = str


class ReadRule(NamedTuple):
    """Grants read access to the fields on the collection under the condition."""

    collection: Collection
    condition: ColumnElement[bool]
    fields: frozenset[Field]


class MutatorRule(NamedTuple):
    """Grants the mutator to the caller owning what the filter names.

    A policy names a mutator once per way of owning what it changes, so the
    rules of a name are read together: the mutator is granted when the caller
    passes one of them.
    """

    name: Mutator
    condition: CEL
    filter: CEL


class CheckSpec(NamedTuple):
    """One object a mutator rule requires the caller to own."""

    collection: Collection
    filter: dict[str, Any]


class Rules(NamedTuple):
    """What the caller's policies grant them."""

    read: list[ReadRule]
    mutators: list[MutatorRule]


class AccessKey(NamedTuple):
    """A field access request."""

    collection: Collection
    uuid: UUID
    field: Field
