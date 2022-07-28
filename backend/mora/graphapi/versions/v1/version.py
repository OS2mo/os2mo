from datetime import date
from typing import Any

from ...version import GraphQLVersion
from ..latest.version import get_version as get_latest_version


def get_version(enable_graphiql: bool, **kwargs: Any) -> GraphQLVersion:
    latest = get_latest_version(enable_graphiql)

    version = GraphQLVersion(
        version=1,
        router=latest.router,
        deprecation_date=date(2023, 1, 1),
    )

    return version
