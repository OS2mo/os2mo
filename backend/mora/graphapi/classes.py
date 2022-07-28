#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
"""GraphQL class related helper functions."""
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import Any
from uuid import UUID

import strawberry

from mora.common import get_connector


@strawberry.type
class GenericError:
    error_message: str


async def terminate_class(uuid: UUID) -> str:
    c = get_connector(virkningfra="-infinity", virkningtil="infinity")
    response = await c.klasse.delete(uuid)
    return f"Class deleted - Response: {response}"
    