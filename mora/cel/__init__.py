# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Common Expression Language (CEL).

See: https://cel.dev
"""

from . import policies
from ._types import CEL

__all__ = ["CEL", "policies"]
