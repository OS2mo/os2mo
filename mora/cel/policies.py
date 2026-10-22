# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Functions to evaluate CEL conditions."""

from functools import lru_cache
from typing import Any
from typing import NewType

from cel_expr_python import cel
from fastapi.encoders import jsonable_encoder

from mora.auth.keycloak.models import Token
from mora.cel._compile import compile
from mora.cel._types import CEL
from mora.cel._types import CelError

# A condition of a policy rule
PolicyCEL = NewType("PolicyCEL", CEL)

# The bindings extension provides `cel.bind`, naming a value once for reuse
_CONFIG = cel.NewEnvConfigFromYaml("""
name: policy
extensions:
  - name: bindings
""")

# A condition names the caller and the arguments of the field it guards
_ENV = cel.NewEnv(
    config=_CONFIG,
    variables={
        "token": cel.Type.Map(cel.Type.STRING, cel.Type.DYN),
        "args": cel.Type.Map(cel.Type.STRING, cel.Type.DYN),
    },
)


@lru_cache(maxsize=2048)
def _compile(condition: PolicyCEL) -> cel.Expression:
    return compile(_ENV, condition)


def validate(condition: str) -> PolicyCEL:
    """Parse the condition, raising a CelError unless it compiles."""
    parsed = PolicyCEL(CEL(condition))
    _compile(parsed)
    return parsed


def evaluate(condition: PolicyCEL, token: Token, args: dict[str, Any]) -> Any:
    activation = _ENV.Activation(
        {
            "token": {
                "uuid": str(token.uuid) if token.uuid is not None else None,
            },
            # CEL cannot accept UUIDs, datetimes, etc.
            "args": jsonable_encoder(args),
        }
    )
    result = _compile(condition).eval(activation)
    if result.type() == cel.Type.ERROR:
        raise CelError(f"condition {condition!r} failed: {result.value()}")
    return result.plain_value()
