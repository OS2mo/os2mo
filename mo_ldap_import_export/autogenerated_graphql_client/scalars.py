from collections.abc import Callable
from typing import Any

SCALARS_PARSE_FUNCTIONS: dict[Any, Callable[[Any], Any]] = {}
SCALARS_SERIALIZE_FUNCTIONS: dict[Any, Callable[[Any], Any]] = {}
