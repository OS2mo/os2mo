# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from ..v21.version import GraphQLVersion as NextGraphQLVersion


class GraphQLVersion(NextGraphQLVersion):
    """GraphQL Version 20.

    Version 21 introduced a breaking change so the first `from_date` or `to_date`
    filter parameters were no longer automatically, implicitly, and forcefully
    inherited in all the following levels of the query.

    Version 20 ensures that the old functionality is still available.
    """

    version = 20
