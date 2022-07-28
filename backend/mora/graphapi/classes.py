#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
"""GraphQL class related helper functions."""
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from uuid import UUID

import strawberry

from backend.mora.graphapi.schema import Class
from backend.ramodels.lora.klasse import Klasse
from mora.common import get_connector


@strawberry.type
class GenericError:
    error_message: str


async def terminate_class(uuid: UUID) -> None:
    c = get_connector(virkningfra="-infinity", virkningtil="infinity")
    return await c.klasse.delete(uuid)


async def edit_class(uuid: UUID) -> Class:
    c = get_connector(virkningfra="-infinity", virkningtil="infinity")
    lora_object = list(await c.klasse.fetch(uuid=uuid))
    print(lora_object)

    # if len(class_list) > 1:
    #     GenericError(f"More than one class found with UUID: {uuid}")
    # elif len(class_list) == 0:
    #     GenericError(f"No classes found with UUID: {uuid}")

    # return Class(
    #     uuid=instance.uuid,
    #     type_=instance.type_,
    #     facet_uuid=instance.facet_uuid,
    #     org_uuid=instance.org_uuid,
    #     scope=instance.scope,
    #     published=instance.published,
    #     parent_uuid=instance.parent_uuid,
    #     example=instance.example,
    #     owner=instance.owner,
    #     name=instance.name,
    #     user_key=instance.user_key,
    # )
