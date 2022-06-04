#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
"""GraphQL facet/class related helper functions."""
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from ramodels.mo import FacetClass
from ramodels.lora import Klasse

from mora import lora
from mora import mapping
from mora.service.handlers import RequestHandler

# --------------------------------------------------------------------------------------
# Code
# --------------------------------------------------------------------------------------


class ClassRequestHandler(RequestHandler):
    role_type = "classx"  # TODO: Remove x when old handler is gone

    async def prepare_create(self, request: dict):
        mo_class = request["class_model"]
        lora_class = Klasse.from_simplified_fields(
            facet_uuid=mo_class.facet_uuid,
            user_key=mo_class.user_key,
            organisation_uuid=mo_class.org_uuid,
            title=mo_class.name,
            uuid=mo_class.uuid,
            scope=mo_class.scope,
        )
        self.payload = jsonable_encoder(lora_class)
        self.uuid = lora_class.uuid

    async def submit(self) -> str:
        # TODO: Currently yields bad input from LoRa
#        mutation {
#          ensure_class(model: {
#            org_uuid: "3b866d97-0b1f-48e0-8078-686d96f430b3",
#            facet_uuid: "182df2a8-2594-4a3f-9103-a9894d5e0c36",
#            user_key: "Fyret",
#            name: "Fyret"
#          })
#        }

        c = lora.Connector()
        if self.request_type == mapping.RequestType.CREATE:
            self.result = await c.klasse.create(self.payload, self.uuid)
        else:
            self.result = await c.klasse.update(self.payload, self.uuid)
        return await super().submit()


async def ensure_class_exists(model: FacetClass) -> UUID:
    req = {"class_model": model}
    request = await ClassRequestHandler.construct(req, mapping.RequestType.CREATE)
    result = await request.submit()
    print(result)
    return result
