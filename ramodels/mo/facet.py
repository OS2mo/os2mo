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
    """
    Attributes:
        name:
        user_key:
        scope:
        org_uuid:
    """

    name: str
    user_key: str
    scope: Optional[str]
    org_uuid: UUID
