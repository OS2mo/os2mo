# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date

from ..v2.version import GraphQLSchema2
from ..v2.version import GraphQLVersion2


class GraphQLSchema1(GraphQLSchema2):
    pass


class GraphQLVersion1(GraphQLVersion2):
    """First pinned version of the GraphQL API."""

    version = 1
    deprecation_date = date(2022, 11, 1)
    schema = GraphQLSchema1
