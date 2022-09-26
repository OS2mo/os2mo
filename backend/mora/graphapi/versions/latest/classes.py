#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from uuid import UUID

from .types import ClassCreateType
from mora import mapping
from mora.graphapi.versions.latest.models import ClassCreate
from mora.service.facet import ClassRequestHandler


# --------------------------------------------------------------------------------------
# Supporting functions for Graphapi mo-classes
# --------------------------------------------------------------------------------------


async def create_class(input: ClassCreate) -> ClassCreateType:

    req_dict = {"facet": str(input.facet_uuid), "class_model": input}

    handler = await ClassRequestHandler.construct(req_dict, mapping.RequestType.CREATE)
    uuid = await handler.submit()

    return ClassCreateType(uuid=UUID(uuid))
