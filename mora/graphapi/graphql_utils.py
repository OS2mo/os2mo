# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import re
import string
from collections.abc import Sequence
from datetime import datetime
from typing import TYPE_CHECKING
from typing import Annotated
from typing import Any
from typing import ForwardRef
from typing import NamedTuple
from typing import TypeAlias
from uuid import UUID

import strawberry
from graphql import FieldNode
from graphql import GraphQLObjectType
from graphql import GraphQLResolveInfo
from graphql import get_named_type
from graphql.execution.collect_fields import collect_sub_fields
from pydantic import ConstrainedStr
from strawberry.types.unset import UnsetType

from mora.db import Collection


class PrintableStr(ConstrainedStr):
    """Custom restricted string type."""

    """
    Define custom type for string to make it
    strict "printable chars" only and min length of 1
    Used in Pydantic models.
    """

    regex = re.compile(rf"^[{string.printable}\n]+$")


class CprNo(ConstrainedStr):
    """Danish CPR No. restricted string type.

    Only allow strings which contain 10 digits from beginning to end
    of the string.
    """

    regex = re.compile(r"^\d{10}$")


# GraphQL field
Field: TypeAlias = str
# GraphQL mutator, as the enum generated from the mutators, which mypy cannot follow
if TYPE_CHECKING:
    MutatorName: TypeAlias = str
else:
    MutatorName = Annotated[
        ForwardRef("Mutator"), strawberry.lazy("mora.graphapi.mutators")
    ]


class AccessKey(NamedTuple):
    """A field access request."""

    collection: Collection
    key: str
    field: Field


class GrantedKey(NamedTuple):
    """A request for the clause granting the fields of a collection."""

    collection: Collection
    fields: frozenset[Field]


class WriteKey(NamedTuple):
    """A mutator access request."""

    mutator: str
    args: dict[str, Any]


class LoadKey(NamedTuple):
    uuid: UUID
    start: datetime | UnsetType | None
    end: datetime | UnsetType | None
    registration_time: datetime | None


def requested_fields(info: GraphQLResolveInfo, path: Sequence[str]) -> frozenset[Field]:
    """The fields requested on the objects at the path below the resolved field.

    The fields are collected as the executor does, thereby following fragments
    and honouring `@skip` and `@include`, while aliases are seen through.

    Args:
        info: The resolve info of the field resolving the objects.
        path: The names of the fields leading from the resolved field to the
            objects, e.g. `["objects"]` for a paged response.

    Returns:
        The names of the fields requested on the objects, without `__typename`.
    """

    def collect(parent: GraphQLObjectType, nodes: list[FieldNode]) -> list[FieldNode]:
        selected = collect_sub_fields(
            info.schema, info.fragments, info.variable_values, parent, nodes
        )
        return [node for nodes in selected.values() for node in nodes]

    parent = get_named_type(info.return_type)
    nodes = info.field_nodes
    for name in path:
        assert isinstance(parent, GraphQLObjectType)
        # The objects may be selected more than once, e.g. under different aliases
        nodes = [node for node in collect(parent, nodes) if node.name.value == name]
        parent = get_named_type(parent.fields[name].type)
    assert isinstance(parent, GraphQLObjectType)
    return frozenset(node.name.value for node in collect(parent, nodes)) - {
        "__typename"
    }
