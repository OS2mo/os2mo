# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from ..v14.version import GraphQLVersion as NextGraphQLVersion
from .mutators import Mutation
from .query import Query


class GraphQLSchema(NextGraphQLVersion.schema):  # type: ignore
    query = Query
    mutation = Mutation


class GraphQLVersion(NextGraphQLVersion):
    """GraphQL Version 13.

    Version 14 introduced a breaking change to all filter variables taken by the
    resolvers, moving them from top-level arguments to a `Filter` object.
    """

    version = 13
    schema = GraphQLSchema
