#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from uuid import UUID

from fastapi import APIRouter
from fastapi import Query
from ramodels.mo import Association


# --------------------------------------------------------------------------------------
# Router
# --------------------------------------------------------------------------------------
router = APIRouter(prefix="/api/v1")

# --------------------------------------------------------------------------------------
# Endpoints
# --------------------------------------------------------------------------------------


@router.get("/association/{uuid}", response_model=Association)
async def get_association(uuid: UUID) -> Association:
    pass


@router.post("/association", response_model=UUID)
async def create_association(in_assoc: Association) -> UUID:
    pass
