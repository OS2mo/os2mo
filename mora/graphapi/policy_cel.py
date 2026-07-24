# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""CEL evaluation for policy rule conditions.

A policy rule may carry an optional CEL (Common Expression Language) condition:
a boolean expression that must additionally hold for the rule to grant access.
The expression is evaluated against a context of variables exposed below.

Currently exposed: the calling actor's ``token``. To expose more (e.g. the
mutation input, the target entity, or the current time), declare the variable
in ``_VARIABLES`` and populate it in :func:`build_activation` -- nothing else
needs to change.
"""

from functools import lru_cache
from typing import Any

from cel_expr_python import cel  # type: ignore[import-untyped]

from mora.auth.keycloak.models import Token

# Variables available to a rule condition. Everything is declared dynamically
# (`DYN`) so expressions may reach into nested fields without static typing,
# and so adding a variable is a one-line change here plus one in
# :func:`build_activation`.
_VARIABLES = {
    "token": cel.Type.DYN,
}

_ENV = cel.NewEnv(variables=_VARIABLES)


@lru_cache(maxsize=1024)
def _compile(condition: str) -> Any:
    """Compile (and cache) a CEL condition into an evaluable program.

    Conditions come from the small, slow-changing set of policy rules, so the
    cache stays bounded and warm across requests.
    """
    return _ENV.compile(condition)


def _token_context(token: Token) -> dict:
    """The ``token`` variable as a CEL-friendly mapping."""
    return {
        "uuid": str(token.uuid) if token.uuid is not None else None,
        "preferred_username": token.preferred_username,
        # A sorted list rather than a set: CEL has no set type, and ordering
        # keeps behaviour deterministic.
        "roles": sorted(token.realm_access.roles),
    }


def build_activation(token: Token) -> Any:
    """Build the CEL activation shared by every condition in a single check.

    The activation holds the variable context and is reused across all matching
    rules' conditions, so it is built once per permission check. Extend the
    returned mapping as the context grows.
    """
    return _ENV.Activation(
        {
            "token": _token_context(token),
        }
    )


def evaluate_condition(condition: str, activation: Any) -> bool:
    """Evaluate a rule's CEL ``condition`` against ``activation`` as a bool."""
    return bool(_compile(condition).eval(activation).value())
