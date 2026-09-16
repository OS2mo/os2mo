# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""CEL evaluation of the expressions a policy rule carries.

A condition is a boolean CEL (Common Expression Language) expression the caller
must pass for the rule to apply, and a filter is a CEL expression naming the
objects the rule reaches: a GraphQL filter on a read rule's collection, and the
`{collection, filter}` specs a mutator rule requires owned.
"""

import json
from functools import lru_cache
from operator import methodcaller
from typing import Any
from typing import TypeAlias

from cel_expr_python import cel  # type: ignore[import-untyped]
from fastapi.encoders import jsonable_encoder

from mora.auth.keycloak.models import Token
from mora.config import Settings
from mora.graphapi.policy import CEL

# The values an expression is evaluated against
Activation: TypeAlias = cel.Activation

# The `bindings` extension provides the `cel.bind` macro, letting an expression
# name a value once and reuse it
_CONFIG = cel.NewEnvConfigFromYaml("""
name: policy
extensions:
  - name: bindings
""")

_ENV = cel.NewEnv(
    config=_CONFIG,
    # The variables an expression may read. Dynamic values: no schema is
    # declared, so any field access compiles
    variables={
        "token": cel.Type.Map(cel.Type.STRING, cel.Type.DYN),
        "settings": cel.Type.Map(cel.Type.STRING, cel.Type.DYN),
        # The arguments of the field, as GraphQL coerced them
        "args": cel.Type.Map(cel.Type.STRING, cel.Type.DYN),
    },
)


@lru_cache(maxsize=2048)
def _compile(expression: CEL) -> cel.Expression:
    """Compile (and cache) a CEL expression into an evaluable program."""
    return _ENV.compile(expression)


def build_activation(
    token: Token, settings: Settings, args: dict[str, Any]
) -> cel.Activation:
    """Build the values every condition and filter is evaluated against."""
    it_system = settings.keycloak_rbac_authoritative_it_system_for_owners
    return _ENV.Activation(
        {
            "token": {
                "uuid": str(token.uuid) if token.uuid is not None else None,
                "preferred_username": token.preferred_username,
                # A list rather than a set: CEL has no set type
                "roles": list(token.realm_access.roles),
            },
            # A curated subset, keeping the interface small and secrets out of it
            "settings": {
                "keycloak_rbac_authoritative_it_system_for_owners": (
                    str(it_system) if it_system is not None else None
                ),
            },
            # CEL reads plain data, while the arguments hold what the scalars
            # of the schema coerced their input into
            "args": jsonable_encoder(args),
        }
    )


def check_condition(condition: CEL, activation: cel.Activation) -> bool:
    """Whether the condition holds. A rule carrying none always applies."""
    if not condition:
        return True
    result = _compile(condition).eval(activation)
    if result.type() != cel.Type.BOOL:
        raise ValueError(
            f"CEL condition {condition!r} result is not boolean: {result.value()}"
        )
    return bool(result.value())


def evaluate_filter(filter: CEL, activation: cel.Activation) -> Any:
    """The value the CEL filter yields, as plain data."""
    result = _compile(filter).eval(activation)
    if result.type() == cel.Type.ERROR:
        raise ValueError(f"failed to evaluate CEL filter {filter!r}: {result.value()}")
    # CEL values are not serializable, so each is unwrapped as it is reached
    return json.loads(json.dumps(result, default=methodcaller("value")))
