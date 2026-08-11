# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""CEL evaluation for policy rule conditions.

A rule's condition is a boolean CEL (Common Expression Language) expression that
must hold for the rule to grant access.
"""

from functools import lru_cache
from typing import Any
from typing import TypeAlias

from cel_expr_python import cel  # type: ignore[import-untyped]

from mora.auth.keycloak.models import Token

# A CEL expression. The empty string means "no expression"
CEL: TypeAlias = str

# Variables available to an expression
_ENV = cel.NewEnv(
    variables={
        # Dynamic values: we declare no schema, so any field access compiles
        "token": cel.Type.Map(cel.Type.STRING, cel.Type.DYN),
    }
)


@lru_cache(maxsize=2048)
def _compile(condition: CEL) -> cel.Expression:
    """Compile (and cache) a CEL condition into an evaluable program."""
    return _ENV.compile(condition)


def _token_context(token: Token) -> dict[str, Any]:
    """The `token` variable as a CEL-friendly mapping."""
    return {
        "uuid": str(token.uuid) if token.uuid is not None else None,
        "preferred_username": token.preferred_username,
        # A list rather than a set: CEL has no set type
        "roles": list(token.realm_access.roles),
    }


def build_activation(token: Token) -> cel.Activation:
    """Build the CEL activation shared by every condition in a single check."""
    return _ENV.Activation({"token": _token_context(token)})


def evaluate_condition(condition: CEL, activation: cel.Activation) -> bool:
    """Evaluate a rule's CEL `condition` against `activation` as a bool."""
    result = _compile(condition).eval(activation)
    if result.type() != cel.Type.BOOL:
        raise ValueError(
            f"CEL condition {condition!r} result is not boolean: {result.value()}"
        )
    return result.value()


def check_condition(condition: CEL, activation: cel.Activation) -> bool:
    """Whether a rule's condition holds. A rule without one always applies."""
    if not condition:
        return True
    return evaluate_condition(condition, activation)
