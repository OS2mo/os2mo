# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Read policies: which fields of which objects a caller may read.

Access is collection-based rather than route-based. It does not matter how
an object is reached, only what the caller may read of it, and that is
decided object by object: the union of the fields granted by the rules
matching it. Reading a field no rule grants fails, just like reading a field
no role grants, unless the read asks to include only the objects it may read
as asked (see `Include`).

Only the address collection is expressed here so far. Everything else is
still gated route by route in `mora.graphapi.rbac_map`.
"""

from collections import defaultdict
from collections.abc import Awaitable
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from textwrap import dedent
from typing import TYPE_CHECKING
from typing import Any
from typing import NamedTuple
from uuid import UUID

import strawberry
from graphql import DocumentNode
from graphql import FieldNode
from graphql import FragmentDefinitionNode
from graphql import FragmentSpreadNode
from graphql import GraphQLError
from graphql import GraphQLIncludeDirective
from graphql import GraphQLInterfaceType
from graphql import GraphQLNamedType
from graphql import GraphQLObjectType
from graphql import GraphQLSchema
from graphql import GraphQLSkipDirective
from graphql import InlineFragmentNode
from graphql import SelectionNode
from graphql import SelectionSetNode
from graphql import get_directive_values
from graphql import get_named_type
from graphql import get_operation_ast
from sqlalchemy import ColumnElement
from sqlalchemy import SQLColumnExpression
from sqlalchemy import and_
from sqlalchemy import distinct
from sqlalchemy import false
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy import true

from mora.auth.keycloak.models import Token
from mora.db import AsyncSession
from mora.db import OrganisationFunktionRegistrering

if TYPE_CHECKING:
    from mora.graphapi.context import MOInfo


@dataclass(frozen=True)
class Collection:
    name: str
    # The GraphQL types whose root is one of the collection's objects
    object_types: frozenset[str]
    # The types wrapping a page of them
    page_types: frozenset[str]
    # The column identifying the objects, which rules select them by
    identifier: SQLColumnExpression[UUID]

    @property
    def types(self) -> frozenset[str]:
        return self.object_types | self.page_types

    def enters(self, parent: str, returned: str) -> bool:
        """Whether a field from *parent* to *returned* leads into the collection."""
        return parent not in self.types and returned in self.types

    def is_object_field(self, parent: str, returned: str) -> bool:
        """Whether a field from *parent* to *returned* reads a field of an object.

        As opposed to leading further into the collection, through the
        containers and pages wrapping its objects.
        """
        return parent in self.object_types and returned not in self.types


ADDRESS = Collection(
    name="address",
    object_types=frozenset(
        {"Address", "AddressResponse", "AddressResponseRegistration"}
    ),
    page_types=frozenset({"AddressResponsePaged"}),
    identifier=OrganisationFunktionRegistrering.organisationfunktion_id,
)

COLLECTIONS: dict[str, Collection] = {ADDRESS.name: ADDRESS}

# The collection each of their GraphQL types belongs to
COLLECTION_OF_TYPE: dict[str, Collection] = {
    name: collection for collection in COLLECTIONS.values() for name in collection.types
}


@dataclass(frozen=True)
class Rule:
    """Grants reading *fields* of the *objects* of a collection.

    None stands for all of them: every field, or every object.
    """

    collection: str
    fields: frozenset[str] | None = None
    objects: ColumnElement[bool] | None = None

    def grants(self, field: str) -> bool:
        return self.fields is None or field in self.fields


@dataclass(frozen=True)
class Policy:
    rules: tuple[Rule, ...]


# The policy of each role. A caller's policies are those of their roles.
ROLE_POLICIES: dict[str, Policy] = {
    "reader": Policy(rules=(Rule(collection="address"),)),
}


def rules_for(token: Token, collection: str) -> list[Rule]:
    """The rules of the caller's policies for *collection*."""
    return [
        rule
        for role in sorted(token.realm_access.roles)
        if role in ROLE_POLICIES
        for rule in ROLE_POLICIES[role].rules
        if rule.collection == collection
    ]


@dataclass(frozen=True)
class Readable:
    """The fields a caller may read of one object; None means every field."""

    fields: frozenset[str] | None

    def __contains__(self, field: str) -> bool:
        return self.fields is None or field in self.fields

    def denies(self, fields: Iterable[str]) -> frozenset[str]:
        if self.fields is None:
            return frozenset()
        return frozenset(fields) - self.fields


async def readable(
    session: AsyncSession,
    rules: Iterable[Rule],
    collection: Collection,
    uuids: Sequence[UUID],
) -> dict[UUID, Readable]:
    """What *rules* grant of each object: the fields of the rules matching it.

    Costs one query per rule limited to some objects; the unconditional ones
    need none.
    """
    granted: dict[UUID, frozenset[str] | None] = {uuid: frozenset() for uuid in uuids}
    for rule in rules:
        matching: Sequence[UUID] = uuids
        if rule.objects is not None:
            matching = (
                await session.scalars(
                    select(distinct(collection.identifier)).where(
                        rule.objects, collection.identifier.in_(uuids)
                    )
                )
            ).all()
        for uuid in matching:
            fields = granted[uuid]
            if fields is None or rule.fields is None:
                granted[uuid] = None
            else:
                granted[uuid] = fields | rule.fields
    return {uuid: Readable(fields) for uuid, fields in granted.items()}


class PolicyKey(NamedTuple):
    collection: str
    uuid: UUID


def policy_loader(
    session: AsyncSession, get_token: Callable[[], Awaitable[Token]]
) -> Callable[[list[PolicyKey]], Awaitable[list[Readable]]]:
    """Batch the lookups of what the caller may read, by collection.

    The answers are the caller's, so the loader lives for one request only.
    """

    async def load(keys: list[PolicyKey]) -> list[Readable]:
        token = await get_token()
        by_collection: dict[str, list[UUID]] = defaultdict(list)
        for key in keys:
            by_collection[key.collection].append(key.uuid)
        loaded: dict[PolicyKey, Readable] = {}
        for name, uuids in by_collection.items():
            rules = rules_for(token, name)
            for uuid, fields in (
                await readable(session, rules, COLLECTIONS[name], uuids)
            ).items():
                loaded[PolicyKey(name, uuid)] = fields
        return [loaded[key] for key in keys]

    return load


class Read(NamedTuple):
    """A read of a collection: the response path of the field leading into it."""

    collection: str
    path: tuple[str, ...]


def requested_fields(
    schema: GraphQLSchema,
    document: DocumentNode,
    operation_name: str | None,
    variables: dict[str, Any] | None,
) -> dict[Read, frozenset[str]]:
    """The fields each read of a collection in the operation asks for.

    Found by walking the operation with the schema's types: through fragments
    and the containers wrapping the objects, but not through the fields
    leading out of the collection, or into it anew.
    """
    operation = get_operation_ast(document, operation_name)
    assert operation is not None
    root = schema.get_root_type(operation.operation)
    assert root is not None
    fragments = {
        definition.name.value: definition
        for definition in document.definitions
        if isinstance(definition, FragmentDefinitionNode)
    }
    requested: dict[Read, set[str]] = defaultdict(set)

    def skipped(node: SelectionNode) -> bool:
        skip = get_directive_values(GraphQLSkipDirective, node, variables)
        include = get_directive_values(GraphQLIncludeDirective, node, variables)
        return bool(skip and skip["if"]) or bool(include and not include["if"])

    def condition(
        node: FragmentDefinitionNode | InlineFragmentNode, default: GraphQLNamedType
    ) -> GraphQLNamedType:
        if node.type_condition is None:
            return default
        type_ = schema.get_type(node.type_condition.name.value)
        assert type_ is not None
        return type_

    def walk(
        selection_set: SelectionSetNode,
        parent: GraphQLNamedType,
        path: tuple[str, ...],
        reads: dict[str, Read],
    ) -> None:
        for selection in selection_set.selections:
            if skipped(selection):
                continue
            if isinstance(selection, FragmentSpreadNode):
                fragment = fragments[selection.name.value]
                walk(fragment.selection_set, condition(fragment, parent), path, reads)
            elif isinstance(selection, InlineFragmentNode):
                walk(selection.selection_set, condition(selection, parent), path, reads)
            elif (
                isinstance(selection, FieldNode)
                and not selection.name.value.startswith("__")
                and isinstance(parent, GraphQLObjectType | GraphQLInterfaceType)
            ):
                name = selection.name.value
                returned = get_named_type(parent.fields[name].type)
                key = path + ((selection.alias or selection.name).value,)
                inner = dict(reads)
                concrete = (
                    [parent]
                    if isinstance(parent, GraphQLObjectType)
                    else schema.get_possible_types(parent)
                )
                for type_ in concrete:
                    for collection in COLLECTIONS.values():
                        if collection.enters(type_.name, returned.name):
                            inner[collection.name] = Read(collection.name, key)
                        elif collection.is_object_field(type_.name, returned.name):
                            requested[reads[collection.name]].add(name)
                if selection.selection_set is not None:
                    walk(selection.selection_set, returned, key, inner)

    walk(operation.selection_set, root, (), {})
    return {read: frozenset(fields) for read, fields in requested.items()}


def fields_read(info: "MOInfo", collection: Collection) -> frozenset[str]:
    """The fields the read at *info* asks for of the objects of *collection*.

    Always `uuid`: the page itself tells which objects exist.
    """
    path = tuple(key for key in info.path.as_list() if isinstance(key, str))
    requested = info.context.requested.get(Read(collection.name, path), frozenset())
    return requested | {"uuid"}


async def check_readable(
    info: "MOInfo", collection: Collection, uuids: Sequence[UUID]
) -> None:
    """Fail the read at *info* unless the caller may read what it asks for of every object.

    Once, naming the fields rather than the objects: a caller expecting to
    read everything learns what their policies lack, while one who may read
    nothing learns nothing about which objects exist.
    """
    fields = fields_read(info, collection)
    loaded = await info.context.dataloaders.policy_loader.load_many(
        [PolicyKey(collection.name, uuid) for uuid in uuids]
    )
    denied = frozenset[str]().union(*(readable.denies(fields) for readable in loaded))
    if denied:
        raise GraphQLError(
            f"No policy approved the access to {', '.join(sorted(denied))}"
        )


@strawberry.enum(
    description=dedent(
        """\
        Which of the objects a read matches to include, given what the caller
        may read of them.
        """
    )
)
class Include(Enum):
    ALL = strawberry.enum_value(
        "ALL",
        description=dedent(
            """\
            Every one. Asking for a field the caller may not read of any of
            them fails the read, so a caller expecting to read everything
            finds out about a lacking policy instead of reading a subset.
            """
        ),
    )
    READABLE = strawberry.enum_value(
        "READABLE",
        description=dedent(
            """\
            Only the objects of which the caller may read every field asked
            for. What the caller may not see is left out, which is what a user
            interface wants.
            """
        ),
    )


async def readable_predicate(
    info: "MOInfo", collection: Collection
) -> ColumnElement[bool]:
    """Select the objects of which the caller may read what the read at *info* asks for.

    Every field asked for must be granted by some rule matching the object.
    """
    rules = rules_for(await info.context.get_token(), collection.name)
    return and_(
        *(
            or_(
                false(),
                *(
                    true() if rule.objects is None else rule.objects
                    for rule in rules
                    if rule.grants(field)
                ),
            )
            for field in sorted(fields_read(info, collection))
        )
    )
