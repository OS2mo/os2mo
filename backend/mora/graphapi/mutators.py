# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
from typing import List
from typing import Optional
from typing import Union
from uuid import UUID

import strawberry
from fastapi.encoders import jsonable_encoder
from more_itertools import one
from ra_utils.generate_uuid import uuid_generator
from ramodels.lora import Organisation as LoraOrganisation

from mora.common import get_connector
from mora.graphapi.schema import Organisation
from mora.service.org import ConfiguredOrganisation


@strawberry.type
class GenericError:
    error_message: str


async def upsert_organisation(
    uuid: Optional[UUID],
    name: str,
    user_key: Optional[str] = None,
    municipality_code: Optional[int] = None,
) -> Organisation:
    if uuid is None:
        generate_uuid = uuid_generator(base="OS2MO")
        uuid = generate_uuid("organisations.__root__")

    if user_key is None:
        user_key = name

    root_organisation = LoraOrganisation.from_simplified_fields(
        uuid=uuid,
        name=name,
        user_key=user_key,
        municipality_code=municipality_code,
    )
    jsonified = jsonable_encoder(
        obj=root_organisation, by_alias=True, exclude={"uuid"}, exclude_none=True
    )
    c = get_connector(virkningfra="-infinity", virkningtil="infinity")
    uuid = await c.organisation.create(jsonified, uuid)
    ConfiguredOrganisation.clear()
    return Organisation(uuid=UUID(uuid), name=name, user_key=user_key)


async def terminate_organisation(uuid: UUID) -> None:
    c = get_connector(virkningfra="-infinity", virkningtil="infinity")
    ConfiguredOrganisation.clear()
    return await c.organisation.delete(uuid)


async def get_organisation_uuids() -> List[UUID]:
    c = get_connector(virkningfra="-infinity", virkningtil="infinity")
    return list(await c.organisation.fetch(bvn="%"))


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_organisation(
        self,
        name: str,
        user_key: Optional[str] = None,
        municipality_code: Optional[int] = None,
    ) -> Union[Organisation, GenericError]:
        orgs = await get_organisation_uuids()
        org_count = len(orgs)

        if org_count != 0:
            return GenericError(error_message="An organisation already exists")

        return await upsert_organisation(None, name, user_key, municipality_code)

    @strawberry.mutation
    async def edit_organisation(
        self,
        uuid: UUID,
        name: str,
        user_key: Optional[str] = None,
        municipality_code: Optional[int] = None,
    ) -> Union[Organisation, GenericError]:
        orgs = await get_organisation_uuids()
        org_count = len(orgs)

        if org_count > 1:
            return GenericError(error_message="Multiple organisations exist")

        if org_count != 1:
            return GenericError(error_message="An organisation does not exist")

        org_uuid = UUID(one(orgs))
        if org_uuid != uuid:
            return GenericError(
                error_message=(
                    "The provided UUID does not match the existing organisation"
                )
            )

        return await upsert_organisation(uuid, name, user_key, municipality_code)

    @strawberry.mutation
    async def remove_organisation(
        self,
        uuid: UUID,
    ) -> Optional[GenericError]:
        await terminate_organisation(uuid)
