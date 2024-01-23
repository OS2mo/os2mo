# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from ..v21.version import GraphQLVersion as NextGraphQLVersion


class GraphQLVersion(NextGraphQLVersion):
    """GraphQL Version 20.

    Prior to this version, the first `from_date` or `to_date` filter parameters were
    automatically, implicitly, and forcefully inherited in all the following levels of
    the query. This is no longer the case.
    """

    version = 20
