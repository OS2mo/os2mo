# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from ..latest.version import LatestGraphQLSchema
from ..latest.version import LatestGraphQLVersion


class GraphQLSchema1(LatestGraphQLSchema):
    """First pinned version of the GraphQL Schema."""

    pass


class GraphQLVersion1(LatestGraphQLVersion):
    """First pinned version of the GraphQL API."""

    version = 1
    deprecation_date = None
    schema = GraphQLSchema1
