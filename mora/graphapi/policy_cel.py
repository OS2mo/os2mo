# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""CEL evaluation for policy rule conditions and entity filters.

A policy rule may carry an optional CEL (Common Expression Language) condition:
a boolean expression that must additionally hold for the rule to grant access.
It may also carry an optional entity filter: a CEL expression returning one or
more access-check specs, each run as a SQL existence check against the entity
being accessed. Both are evaluated against a context of variables exposed
below.
"""

from functools import lru_cache
from typing import Any

from cel_expr_python import cel  # type: ignore[import-untyped]

from mora.auth.keycloak.models import Token

# Variables available to a rule condition/filter. Everything is declared
# dynamically (`DYN`) so expressions may reach into nested fields without static
# typing, and so adding a variable is a one-line change here plus one in the
# relevant activation builder.
#
# `input` is the mutator's argument (the object being created/changed) and is
# only populated for rule *filter* expressions (see build_filter_base_vars); a
# condition that references it without that context errors, which is intended.
#
# `actor` (the resolved calling employee's uuid) and `current` (the existing DB
# object) are declared here so filters may reference them, but they are resolved
# *lazily*: expensive to compute and usually unused, they are bound on demand
# only when the executed CEL path dereferences them (see evaluate_filter).
_VARIABLES = {
    "token": cel.Type.DYN,
    "input": cel.Type.DYN,
    "actor": cel.Type.DYN,
    "current": cel.Type.DYN,
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


def build_filter_base_vars(token: Token, input: Any) -> dict:
    """The eagerly-bound variables for a rule's entity filter expression.

    Like :func:`build_activation` but as a plain mapping (so lazily-resolved
    variables can be added to it) and also exposing ``input`` -- the mutator's
    argument as a plain mapping -- so the filter can correlate the grant with
    both the caller and what they submitted. The lazy ``actor``/``current`` are
    intentionally *not* bound here; see :func:`evaluate_filter`.
    """
    return {
        "token": _token_context(token),
        "input": input,
    }


def evaluate_condition(condition: str, activation: Any) -> bool:
    """Evaluate a rule's CEL ``condition`` against ``activation`` as a bool."""
    return bool(_compile(condition).eval(activation).value())


def _to_native(value: Any) -> Any:
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
    return value  # pragma: no cover - defensive: CEL values are scalar/map/list


# An unbound *declared* variable makes the whole eval result an ERROR whose value
# is this string (naming the missing variable). It is distinct from a genuine
# evaluation error (division by zero, key/index error, ...), some of which also
# carry an "UNKNOWN:" prefix -- hence the full, specific prefix below.
_UNKNOWN_VAR_PREFIX = 'UNKNOWN: No value with name "'


def _unknown_variable(result: Any) -> str | None:
    """Name of the unbound variable that made ``result`` unknown, else ``None``.

    Referencing a declared-but-unbound variable does not raise; it yields an
    ERROR result whose message names the variable. Any *other* ERROR is a genuine
    evaluation failure and must fail hard, so we match the exact message prefix
    rather than the generic ERROR type or a bare ``"UNKNOWN:"``.
    """
    if result.type() != cel.Type.ERROR:
        return None
    message = str(result.value())
    if not message.startswith(_UNKNOWN_VAR_PREFIX):
        return None
    name, _, _ = message[len(_UNKNOWN_VAR_PREFIX) :].partition('"')
    return name


def _normalize_check_specs(native: Any) -> list[dict]:
    """Normalize a filter expression's result to a list of check-spec maps.

    A single map is wrapped into a one-element list; a list must contain only
    maps. Anything else raises ``ValueError`` (fail hard).
    """
    if isinstance(native, dict):
        return [native]
    if isinstance(native, list):
        if not all(isinstance(item, dict) for item in native):
            raise ValueError("CEL filter list must contain only check-spec maps")
        return native
    raise ValueError(
        "CEL filter must return a check-spec map or a list of them, got "
        f"{type(native).__name__}"
    )


async def evaluate_filter(
    expression: str, base_vars: dict, loaders: dict
) -> list[dict]:
    """Evaluate a rule's CEL filter ``expression`` to a list of check-specs.

    ``base_vars`` are the eagerly-bound variables (``token``/``input``).
    ``loaders`` maps a lazily-resolved variable name (``actor``/``current``) to
    an async zero-argument callable producing its value; a loader is awaited
    only when the executed CEL path dereferences that variable
    (branch-sensitive), after which the expression is re-evaluated. Resolution
    is bounded by the number of lazy variables.

    Any failure -- a compile/eval error, an unresolvable variable or a
    non-map/list result -- raises ``ValueError``, so a misconfigured filter fails
    hard rather than silently denying.
    """
    try:
        program = _compile(expression)
    except Exception as exc:  # noqa: BLE001 - surface any compile failure uniformly
        raise ValueError(f"failed to compile CEL filter: {exc}") from exc

    bound = dict(base_vars)
    # Each round resolves at most one lazy variable, so the loop is bounded.
    for _ in range(len(loaders) + 1):
        # eval yields an ERROR *value* for bad expressions; it rarely raises.
        try:
            result = program.eval(_ENV.Activation(bound))
        except Exception as exc:  # noqa: BLE001 # pragma: no cover
            raise ValueError(f"failed to evaluate CEL filter: {exc}") from exc
        missing = _unknown_variable(result)
        if missing is None:
            if result.type() == cel.Type.ERROR:
                # A genuine evaluation error (not a missing variable): fail hard.
                raise ValueError(f"failed to evaluate CEL filter: {result.value()}")
            return _normalize_check_specs(_to_native(result.value()))
        # Declared variables are all bound eagerly or resolvable via a loader.
        if missing not in loaders:  # pragma: no cover
            raise ValueError(f'CEL filter references unknown variable "{missing}"')
        if missing in bound:  # pragma: no cover - defensive: loader made no progress
            raise ValueError(f'CEL filter variable "{missing}" could not be resolved')
        bound[missing] = await loaders[missing]()
    raise ValueError(  # pragma: no cover - unreachable: bounded by lazy-var count
        "CEL filter lazy-variable resolution did not converge"
    )
