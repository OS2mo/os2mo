#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import Optional
from uuid import UUID

from ramodels.mo._shared import MOBase

# --------------------------------------------------------------------------------------
# Facet models
# --------------------------------------------------------------------------------------


class FacetClass(MOBase):
    """Payload model for Klasses to be created under the given Facet.

    Attributes:
        name (str): Human-readable name
        user_key (str): Short, unique key
        scope (Optional[str]): Representation of Klasse type
        org_uuid (UUID): Organisation UUID
    """

    name: str
    user_key: str
    scope: Optional[str]
    org_uuid: UUID
