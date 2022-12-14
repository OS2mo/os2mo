# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from fastapi.encoders import jsonable_encoder

from .models import OrganisationCreate
from .types import OrganisationType
from mora import lora
from ramodels.lora.organisation import Organisation


async def create_organisation(input: OrganisationCreate) -> OrganisationType:
    # Convert input to LoRa payload
    root_organisation = Organisation.from_simplified_fields(
        name=input.name,
        user_key=input.name,
    )

    jsonified = jsonable_encoder(
        obj=root_organisation, by_alias=True, exclude={"uuid"}, exclude_none=True
    )

    # Create the ORG in LoRa
    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
    uuid = await c.organisation.create(jsonified)

    # Return
    return OrganisationType(uuid=uuid)
