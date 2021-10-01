#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import Any

# --------------------------------------------------------------------------------------
# Exceptions
# --------------------------------------------------------------------------------------


class ISOParseError(ValueError):
    """Error to raise when parsing of ISO-8601 datetime strings fails."""

    def __init__(self, fail_value: Any) -> None:
        """Initialise with a suiting description including the failing value."""
        super().__init__(
            f"Unable to parse '{fail_value}' as an ISO-8601 datetime string"
        )
