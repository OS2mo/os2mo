# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections import defaultdict
from collections.abc import Callable
from functools import partial
from typing import Any
from typing import Literal

from cel_expr_python import cel  # type: ignore[import-untyped]
from graphql import coerce_input_value
from more_itertools import one
from pydantic import BaseModel
from pydantic import parse_raw_as
from sqlalchemy import ColumnElement
from sqlalchemy import and_
from sqlalchemy import exists
from sqlalchemy import or_
from sqlalchemy import select
from strawberry.dataloader import DataLoader
from strawberry.types.arguments import convert_argument

from mora import db
from mora.db import AsyncSession
from mora.graphapi import resolvers
from mora.graphapi.context import MOInfo
from mora.graphapi.policy_cel import CEL
from mora.graphapi.policy_cel import evaluate_filter

POLICY_LOADER_KEY = "policy_loader"


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


async def policy_rules_resolver(
    session: AsyncSession, keys: list[frozenset[str]]
) -> list[dict[tuple[str, str], list[tuple[CEL, CEL]]]]:
    """The applicable rules for the caller's roles."""
    # The loader is cached per request, and the token never changes per request,
    # so we only ever get called with one set of roles
    roles = one(keys)
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
    )
    rows = (await session.execute(query)).all()
    index: dict[tuple[str, str], list[tuple[CEL, CEL]]] = defaultdict(list)
    for row in rows:
        index[(row.type, row.field)].append((row.condition, row.filter))
    return [index]


def get_policy_loaders(session: AsyncSession) -> dict[str, DataLoader]:
    return {
        POLICY_LOADER_KEY: DataLoader(load_fn=partial(policy_rules_resolver, session))
    }
