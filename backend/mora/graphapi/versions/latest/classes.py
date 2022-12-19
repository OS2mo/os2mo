# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from .types import UUIDReturn
from mora import mapping
from mora.graphapi.versions.latest.models import ClassCreate
from mora.service.facet import ClassRequestHandler


async def create_class(input: ClassCreate) -> UUIDReturn:

    req_dict = {"facet": str(input.facet_uuid), "class_model": input}

    handler = await ClassRequestHandler.construct(req_dict, mapping.RequestType.CREATE)
    uuid = await handler.submit()

    return UUIDReturn(uuid=UUID(uuid))
