# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from functools import partial
from uuid import UUID

import strawberry
from more_itertools import flatten

from ..latest.permissions import gen_read_permission
from ..latest.permissions import IsAuthenticatedPermission
from ..v13.resolvers import ClassResolver
from ..v13.resolvers import FacetResolver
from ..v13.resolvers import ITSystemResolver
from ..v13.resolvers import Resolver
from ..v13.schema import Class
from ..v13.schema import Facet
from ..v13.schema import ITSystem
from ..v13.schema import Paged
from ..v17.version import to_paged
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
