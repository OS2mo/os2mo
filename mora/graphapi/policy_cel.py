# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Functions to evaluate CEL conditions."""

from functools import lru_cache
from typing import Any
from typing import TypeAlias

from cel_expr_python import cel
from fastapi.encoders import jsonable_encoder

from mora.auth.keycloak.models import Token

# A Common Expression Language expression
CEL: TypeAlias = str

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
def _compile(condition: CEL) -> Any:
    return _ENV.compile(condition)


def evaluate(condition: CEL, token: Token, args: dict[str, Any]) -> Any:
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
        raise ValueError(f"condition {condition!r} failed: {result.value()}")
    return result.plain_value()
