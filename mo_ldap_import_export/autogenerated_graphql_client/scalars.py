from typing import Any
from typing import Callable
from typing import Dict

SCALARS_PARSE_FUNCTIONS: Dict[Any, Callable[[Any], Any]] = {}
SCALARS_SERIALIZE_FUNCTIONS: Dict[Any, Callable[[Any], Any]] = {}
