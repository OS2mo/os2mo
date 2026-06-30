# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""CEL evaluation for policy rule conditions.

A policy rule may carry an optional CEL (Common Expression Language) condition:
a boolean expression that must additionally hold for the rule to grant access.
The expression is evaluated against a context of variables exposed below.

Currently exposed: the calling actor's ``token`` and the ``permission`` (the
role the accessed field requires under legacy RBAC). To expose more (e.g. the
mutation input, the target entity, or the current time), declare the variable
in ``_VARIABLES`` and populate it in :func:`build_activation` -- nothing else
needs to change.
"""

from functools import lru_cache

from cel_expr_python import cel

from mora.auth.keycloak.models import Token

# Variables available to a rule condition/filter. Everything is declared
# dynamically (`DYN`) so expressions may reach into nested fields without static
# typing, and so adding a variable is a one-line change here plus one in the
# relevant activation builder.
#
# `input` is the mutator's argument (the object being created/changed) and is
# only populated for rule *filter* expressions (see build_filter_activation); a
# condition that references it without that context errors, which is intended.
_VARIABLES = {
    "token": cel.Type.DYN,
    "permission": cel.Type.DYN,
    "input": cel.Type.DYN,
}

_ENV = cel.NewEnv(variables=_VARIABLES)


@lru_cache(maxsize=1024)
def _compile(condition: str):
    """Compile (and cache) a CEL condition into an evaluable program.

    Conditions come from the small, slow-changing set of policy rules, so the
    cache stays bounded and warm across requests.
    """
    return _ENV.compile(condition)


def validate_condition(condition: str) -> None:
    """Raise ``ValueError`` if ``condition`` is not a compilable CEL expression.

    Called when declaring a rule so malformed conditions are rejected up front
    rather than failing at permission-check time.
    """
    try:
        _compile(condition)
    except Exception as exc:  # noqa: BLE001 - surface any compile failure uniformly
        raise ValueError(f"Invalid CEL condition: {exc}") from exc


def validate_filter(expression: str) -> None:
    """Raise ``ValueError`` if ``expression`` is not a compilable CEL expression.

    A rule's entity filter is a CEL expression returning a filter map. Its shape
    cannot be checked statically (it depends on ``token``/``input``), so declare
    time only compile-checks it; an expression that compiles but returns a
    non-filter fails hard at permission-check time (see :func:`evaluate_filter`).
    """
    try:
        _compile(expression)
    except Exception as exc:  # noqa: BLE001 - surface any compile failure uniformly
        raise ValueError(f"Invalid CEL filter expression: {exc}") from exc


def _token_context(token: Token) -> dict:
    """The ``token`` variable as a CEL-friendly mapping."""
    return {
        "uuid": str(token.uuid) if token.uuid is not None else None,
        "preferred_username": token.preferred_username,
        # A sorted list rather than a set: CEL has no set type, and ordering
        # keeps behaviour deterministic.
        "roles": sorted(token.realm_access.roles),
    }


def build_activation(token: Token, permission: str | None = None):
    """Build the CEL activation shared by every condition in a single check.

    The activation holds the variable context and is reused across all matching
    rules' conditions, so it is built once per permission check. Extend the
    returned mapping as the context grows.

    ``permission`` is the role the accessed field requires under legacy RBAC
    (e.g. ``"read_employee"``); a null one is exposed as the empty string so a
    condition like ``permission in token.roles`` simply evaluates false.
    """
    return _ENV.Activation(
        {
            "token": _token_context(token),
            "permission": permission or "",
        }
    )


def build_filter_activation(token: Token, input: dict, permission: str | None = None):
    """Build the CEL activation for a rule's entity filter expression.

    Like :func:`build_activation` but also exposes ``input`` -- the mutator's
    argument (the object being created/changed) as a plain mapping -- so the
    filter can correlate the grant with both the caller and what they submitted.
    """
    return _ENV.Activation(
        {
            "token": _token_context(token),
            "input": input,
            "permission": permission or "",
        }
    )


def evaluate_condition(condition: str, activation) -> bool:
    """Evaluate a rule's CEL ``condition`` against ``activation`` as a bool."""
    return bool(_compile(condition).eval(activation).value())


def _to_native(value):
    """Recursively unwrap a CEL value into plain Python types.

    ``.value()`` only converts the top level; nested maps/lists come back as CEL
    accessor wrappers (which themselves expose ``.value()``), so we recurse to
    get plain dicts/lists/scalars the filter deserializers can consume.
    """
    if value is None or isinstance(value, str | bytes | bool | int | float):
        return value
    if isinstance(value, dict):
        return {key: _to_native(val) for key, val in value.items()}
    if isinstance(value, list | tuple):
        return [_to_native(item) for item in value]
    if hasattr(value, "value") and callable(value.value):
        return _to_native(value.value())
    return value


def evaluate_filter(expression: str, activation) -> dict:
    """Evaluate a rule's CEL filter ``expression`` to a filter mapping.

    The expression must return a CEL map (the serialized MO filter). Anything
    else -- a compile/eval failure or a non-map result -- raises ``ValueError``,
    so a misconfigured filter fails hard rather than silently denying.
    """
    try:
        result = _to_native(_compile(expression).eval(activation).value())
    except ValueError:
        raise
    except Exception as exc:  # noqa: BLE001 - surface any failure uniformly
        raise ValueError(f"failed to evaluate CEL filter: {exc}") from exc
    if not isinstance(result, dict):
        raise ValueError(
            "CEL filter expression must return a map (filter), got "
            f"{type(result).__name__}"
        )
    return result
