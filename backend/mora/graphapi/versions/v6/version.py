# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from functools import partial
from uuid import UUID

import strawberry
from more_itertools import flatten

from ..latest.permissions import gen_read_permission
from ..latest.permissions import IsAuthenticatedPermission
from ..latest.query import to_paged
from ..latest.resolvers import ClassResolver
from ..latest.resolvers import FacetResolver
from ..latest.resolvers import ITSystemResolver
from ..latest.resolvers import Resolver
from ..latest.schema import Class
from ..latest.schema import Facet
from ..latest.schema import ITSystem
from ..latest.schema import Paged
from ..v7.version import GraphQLVersion as NextGraphQLVersion


def to_list(resolver: Resolver, result: dict[UUID, list[dict]]) -> list:
    return list(flatten(result.values()))


to_paged_list = partial(to_paged, result_transformer=to_list)


@strawberry.type(description="Entrypoint for all read-operations")
class Query(NextGraphQLVersion.schema.query):  # type: ignore[name-defined]
    # Classes
    # -------
    classes: Paged[Class] = strawberry.field(
        resolver=to_paged_list(ClassResolver()),
        description="Get a list of all classes, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # Facets
    # ------
    facets: Paged[Facet] = strawberry.field(
        resolver=to_paged_list(FacetResolver()),
        description="Get a list of all facets, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("facet")],
    )

    # ITSystems
    # ---------
    itsystems: Paged[ITSystem] = strawberry.field(
        resolver=to_paged_list(ITSystemResolver()),
        description="Get a list of all ITSystems, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("itsystem")],
    )


class GraphQLSchema(NextGraphQLVersion.schema):  # type: ignore
    """Version 6 of the GraphQL Schema.

    Version 7 introduced a breaking change to the response format of `facet`, `class`
    and `itsystem`, ensuring they now return a format similar to the rest of the
    entities.
    Version 6 ensures that the old functionality is still available.
    """

    query = Query


class GraphQLVersion(NextGraphQLVersion):
    """GraphQL Version 6."""

    version = 6
    schema = GraphQLSchema
