# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Common Expression Language (CEL).

See: https://cel.dev
"""

from . import policies
from . import rolebinding_rules
from ._types import CEL
from ._types import CelError

__all__ = ["CEL", "CelError", "policies", "rolebinding_rules"]
