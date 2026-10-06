# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The CEL environment that rolebinding rules are written against."""

from typing import Any
from typing import NewType

from cel_expr_python.cel import Env
from cel_expr_python.cel import Expression
from cel_expr_python.cel import NewEnv
from cel_expr_python.cel import Type

from mora.cel import CEL

# An expression of a rolebinding rule, matching the IT-users to grant the role to
RolebindingRuleCEL = NewType("RolebindingRuleCEL", CEL)

ROOT_VARIABLE = "ituser"


class CelError(ValueError):
    """The expression is not one the rolebinding rule engine can run."""


def _environment() -> Env:
    return NewEnv(variables={ROOT_VARIABLE: Type.Map(Type.STRING, Type.DYN)})


_ENV = _environment()


def compile(expression: str) -> Expression:
    if not expression.strip():
        raise CelError("the expression is empty")

    try:
        compiled = _ENV.compile(expression)
    except Exception as error:
        raise CelError(str(error)) from error

    return_type = compiled.return_type()
    if return_type != Type.BOOL:
        raise CelError(
            f"the expression must be true or false, but is {return_type.name().lower()}"
        )

    return compiled


def validate(expression: str) -> RolebindingRuleCEL:
    """Compile *expression* and run it against a test object."""

    _SMOKE_TEST: dict[str, Any] = {
        ROOT_VARIABLE: {
            "person": {"uuid": "00000000-0000-0000-0000-000000000000"},
            "engagement": {
                "job_function": {"uuid": "00000000-0000-0000-0000-000000000000"},
                "engagement_type": {"uuid": "00000000-0000-0000-0000-000000000000"},
                "org_unit": {
                    "uuid": "00000000-0000-0000-0000-000000000000",
                    "path_uuids": [
                        "00000000-0000-0000-0000-000000000000",
                        "00000000-0000-0000-0000-000000000000",
                    ],
                },
            },
        }
    }

    compiled = compile(expression)
    result = compiled.eval(data=_SMOKE_TEST)
    if result.type() == Type.ERROR:
        raise CelError(result.plain_value())
    return RolebindingRuleCEL(CEL(expression))
