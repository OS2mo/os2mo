# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""What the policies of a caller grant them, as one operation sees it."""

from typing import Any
from typing import NamedTuple
from typing import TypeAlias

# OIDC token role
Role: TypeAlias = str
# GraphQL collection
Collection: TypeAlias = str
# GraphQL mutator
Mutator: TypeAlias = str
# A CEL expression. The empty string means "no expression"
CEL: TypeAlias = str


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
