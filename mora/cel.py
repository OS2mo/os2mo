# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Common Expression Language (CEL).

See: https://cel.dev
"""

from typing import NewType

# A Common Expression Language expression
CEL = NewType("CEL", str)
