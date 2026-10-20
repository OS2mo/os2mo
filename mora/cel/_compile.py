# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from cel_expr_python import cel

from mora.cel._types import CelError


def compile(env: cel.Env, expression: str) -> cel.Expression:
    """Compile the expression in the environment, raising a CelError on failure."""
    if not expression.strip():
        raise CelError("the expression is empty")

    try:
        compiled = env.compile(expression)
    except RuntimeError as error:
        raise CelError(str(error)) from error
    return compiled
