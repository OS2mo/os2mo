# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The CEL environment that rolebinding rules are written against."""

from typing import Any

from cel_expr_python.cel import Env
from cel_expr_python.cel import Expression
from cel_expr_python.cel import NewEnv
from cel_expr_python.cel import Type

ROOT_VARIABLE = "ituser"


class CelError(ValueError):
    """The expression is not one the rolebinding rule engine can run."""


def _environment() -> Env:
    return NewEnv(variables={ROOT_VARIABLE: Type.Map(Type.STRING, Type.DYN)})


_ENV = _environment()


def _readable_value(value: Any) -> str:
    message = str(value).strip()
    for prefix in ("NOT_FOUND: ", "INVALID_ARGUMENT: "):
        message = message.removeprefix(prefix)
    return message


def _readable(error: Exception) -> str:
    message = str(error).strip()
    for prefix in ("INVALID_ARGUMENT: ", "ERROR: "):
        message = message.removeprefix(prefix)
    return message.splitlines()[0].strip()


def compile(expression: str) -> Expression:
    if not expression.strip():
        raise CelError("the expression is empty")

    try:
        compiled = _ENV.compile(expression)
    except Exception as error:
        raise CelError(_readable(error)) from error

    return_type = compiled.return_type().name()
    if return_type != "BOOL":
        raise CelError(
            f"the expression must be true or false, but is {return_type.lower()}"
        )

    return compiled


def validate(expression: str) -> None:
    """Compile *expression* and run it against a test object."""

    _SMOKE_TEST: dict[str, Any] = {
        ROOT_VARIABLE: {
            "person": {"uuid": "00000000-0000-0000-0000-000000000000"},
            "engagement": {
                "job_function": {"uuid": "00000000-0000-0000-0000-000000000000"},
                "engagement_type": {"uuid": "00000000-0000-0000-0000-000000000000"},
                "org_unit": {
                    "uuid": "00000000-0000-0000-0000-000000000000",
                    "path_uuids": ["00000000-0000-0000-0000-000000000000"],
                },
            },
        }
    }

    compiled = compile(expression)
    result = compiled.eval(data=_SMOKE_TEST)
    if result.type().name() == "ERROR":
        raise CelError(_readable_value(result.plain_value()))
