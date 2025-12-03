from collections.abc import Callable
from datetime import datetime
from typing import Any

from fastramqpi.ariadne import parse_graphql_datetime

SCALARS_PARSE_FUNCTIONS: dict[Any, Callable[[Any], Any]] = {
    datetime: parse_graphql_datetime
}
SCALARS_SERIALIZE_FUNCTIONS: dict[Any, Callable[[Any], Any]] = {}
