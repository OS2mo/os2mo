# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from ..latest.version import LatestGraphQLSchema
from ..latest.version import LatestGraphQLVersion


class GraphQLSchema4(LatestGraphQLSchema):
    """Latest GraphQL Schema, exposed as a version.

    When adding breaking changes, modify this schema to maintain compatibility for the
    version.
    """


class GraphQLVersion4(LatestGraphQLVersion):
    """Latest GraphQL version."""

    version = 4
    schema = GraphQLSchema4
