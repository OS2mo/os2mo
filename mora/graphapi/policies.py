# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections import defaultdict
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Iterator
from typing import Any
from typing import Literal

from cel_expr_python import cel  # type: ignore[import-untyped]
from graphql import DocumentNode
from graphql import FieldNode
from graphql import GraphQLCompositeType
from graphql import GraphQLInterfaceType
from graphql import GraphQLSchema
from graphql import GraphQLUnionType
from graphql import TypeInfo
from graphql import TypeInfoVisitor
from graphql import Visitor
from graphql import coerce_input_value
from graphql import visit
from pydantic import BaseModel
from pydantic import parse_raw_as
from sqlalchemy import ColumnElement
from sqlalchemy import and_
from sqlalchemy import exists
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy import tuple_
from strawberry.types.arguments import convert_argument

from mora import db
from mora.auth.keycloak.models import Token
from mora.db import AsyncSession
from mora.graphapi import resolvers
from mora.graphapi.context import MOInfo
from mora.graphapi.policy_cel import CEL
from mora.graphapi.policy_cel import build_activation
from mora.graphapi.policy_cel import evaluate_filter
from mora.graphapi.policy_cel import settle_condition

# The collections a check-spec may name, each the predicate selecting its
# matching objects. The filter is read off the predicate's own signature
COLLECTIONS: dict[str, Callable[..., ColumnElement]] = {
    "employee": resolvers.employee_predicate,
    "org_unit": resolvers.organisation_unit_predicate,
    "address": resolvers.address_predicate,
    "association": resolvers.association_predicate,
    "engagement": resolvers.engagement_predicate,
    "ituser": resolvers.it_user_predicate,
    "kle": resolvers.kle_predicate,
    "leave": resolvers.leave_predicate,
    "manager": resolvers.manager_predicate,
    "owner": resolvers.owner_predicate,
    "related_unit": resolvers.related_unit_predicate,
    "rolebinding": resolvers.rolebinding_predicate,
}


def _concrete_types(schema: GraphQLSchema, type: GraphQLCompositeType) -> Iterator[str]:
    """The type itself and, if abstract, every type it stands for.

    A resolver is handed the concrete type, while a document may name an
    interface or union instead.
    """
    yield type.name
    if isinstance(type, GraphQLInterfaceType):
        implementations = schema.get_implementations(type)
        for object_type in implementations.objects:
            yield object_type.name
        for interface in implementations.interfaces:
            yield from _concrete_types(schema, interface)
    elif isinstance(type, GraphQLUnionType):
        for member in type.types:
            yield member.name


def _relevant_rules(
    index: dict[tuple[str, str], list[tuple[CEL, CEL]]], type: str, field: str
) -> list[tuple[CEL, CEL]]:
    """The rules matching this exact (type, field), or a wildcard in either part."""
    return (
        index.get((type, field), [])
        + index.get((type, "*"), [])
        + index.get(("*", field), [])
        + index.get(("*", "*"), [])
    )


def build_plan(
    index: dict[tuple[str, str], list[tuple[CEL, CEL]]],
    token: Token,
    fields: Iterable[tuple[str, str]],
) -> dict[tuple[str, str], list[tuple[CEL, CEL]]]:
    """The index, reduced to the rules of each field that only the call can decide.

    Every condition is put to the evaluator against the token alone: a rule it
    fails is dropped, and a rule it settles is kept without it.
    """
    # The call is not known yet, so the arguments are left out of the activation
    activation = build_activation(token)
    return {
        (type, field): [
            ("" if settled else condition, filter)
            for condition, filter in _relevant_rules(index, type, field)
            if (settled := settle_condition(condition, activation)) is not False
        ]
        for type, field in fields
    }


def collect_accessed_fields(
    schema: GraphQLSchema, document: DocumentNode
) -> frozenset[tuple[str, str]]:
    """Every `(type, field)` the document can reach.

    The whole document is walked, fragments and unexecuted operations included:
    over-collecting only widens the rules fetched, whereas a field left out finds
    no rules at all.
    """
    accessed: set[tuple[str, str]] = set()
    type_info = TypeInfo(schema)

    class Collector(Visitor):
        def enter_field(self, node: FieldNode, *_args: Any) -> None:
            parent = type_info.get_parent_type()
            # The document is validated by now, so every field is selected on a type
            assert parent is not None
            for type in _concrete_types(schema, parent):
                accessed.add((type, node.name.value))

    visit(document, TypeInfoVisitor(type_info, Collector()))
    return frozenset(accessed)


class CheckSpec(BaseModel):
    """One object a rule's filter requires to exist."""

    collection: Literal[tuple(COLLECTIONS)]  # type: ignore[valid-type]
    filter: dict[str, Any]

    class Config:
        extra = "forbid"

    @property
    def filter_type(self) -> type:
        """The MO filter type this spec's filter map is coerced into.

        The one the predicate takes, so the two cannot disagree.
        """
        return self.predicate.__annotations__["filter"]

    @property
    def predicate(self) -> Callable[..., ColumnElement]:
        """The collection's resolver predicate, selecting the matching objects."""
        return COLLECTIONS[self.collection]

    def to_filter(self, info: MOInfo) -> Any:
        """Convert the collection and filter dict to the resolver's filter type."""
        schema = info.schema
        coerce_input_value(
            self.filter, schema.schema_converter.from_input_object(self.filter_type)
        )
        return convert_argument(
            self.filter,
            self.filter_type,
            scalar_registry=schema.schema_converter.scalar_registry,
            config=schema.config,
        )


async def entity_filter_grants(
    filter: CEL, info: MOInfo, activation: cel.Activation
) -> bool:
    """Whether every check-spec the rule's `filter` yields matches an object."""
    specs = parse_raw_as(list[CheckSpec], evaluate_filter(filter, activation))
    if not specs:
        return False
    # Every spec must hold, AND-ed into one EXISTS statement so a bulk mutation
    # costs a single round trip
    matches = (
        exists().where(spec.predicate(info=info, filter=spec.to_filter(info)))
        for spec in specs
    )
    all_match = select(and_(*matches))
    return bool(await info.context.session.scalar(all_match))


async def load_rules(
    session: AsyncSession,
    roles: frozenset[str],
    fields: frozenset[tuple[str, str]],
) -> dict[tuple[str, str], list[tuple[CEL, CEL]]]:
    """The active rules an actor holding `roles` has over `fields`."""
    query = (
        select(
            db.PolicyRule.type,
            db.PolicyRule.field,
            db.PolicyRule.condition,
            db.PolicyRule.filter,
        )
        .join(db.Policy)
        .where(db.Policy.active)
        .where(
            exists().where(
                db.PolicyActor.policy_fk == db.Policy.id,
                or_(
                    db.PolicyActor.kind == db.PolicyActorKind.all,
                    and_(
                        db.PolicyActor.kind == db.PolicyActorKind.role,
                        db.PolicyActor.value.in_(roles),
                    ),
                ),
            )
        )
        .where(
            # A wildcard rule matches fields no document can name, so it is
            # fetched whatever the operation asks for
            or_(
                db.PolicyRule.type == "*",
                db.PolicyRule.field == "*",
                tuple_(db.PolicyRule.type, db.PolicyRule.field).in_(fields),
            )
        )
    )
    rows = (await session.execute(query)).all()
    index: dict[tuple[str, str], list[tuple[CEL, CEL]]] = defaultdict(list)
    for row in rows:
        index[(row.type, row.field)].append((row.condition, row.filter))
    return index
