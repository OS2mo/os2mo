# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from ..latest.query import Query
from ..latest.version import LatestGraphQLSchema
from ..latest.version import LatestGraphQLVersion


class GraphQLSchema3(LatestGraphQLSchema):
    query = Query


class GraphQLVersion3(LatestGraphQLVersion):
    """Latest versioned GraphQL API."""

    version = 3
    deprecation_date = None
    schema = GraphQLSchema3
