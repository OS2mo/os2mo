# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import NewType

# A Common Expression Language expression
CEL = NewType("CEL", str)


class CelError(ValueError):
    """The expression is not one the CEL environment can compile or evaluate."""
