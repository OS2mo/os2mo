# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Functions to evaluate CEL conditions."""

from functools import lru_cache
from typing import Any
from typing import TypeAlias

from cel_expr_python import cel

from mora.auth.keycloak.models import Token

# A Common Expression Language expression
CEL: TypeAlias = str

# A condition names the caller alone
_ENV = cel.NewEnv(variables={"token": cel.Type.Map(cel.Type.STRING, cel.Type.DYN)})


@lru_cache(maxsize=2048)
def _compile(condition: CEL) -> Any:
    return _ENV.compile(condition)


def evaluate(condition: CEL, token: Token) -> Any:
    activation = _ENV.Activation(
        {
            "token": {
                "uuid": str(token.uuid) if token.uuid is not None else None,
            }
        }
    )
    result = _compile(condition).eval(activation)
    if result.type() == cel.Type.ERROR:
        raise ValueError(f"condition {condition!r} failed: {result.value()}")
    return result.plain_value()
