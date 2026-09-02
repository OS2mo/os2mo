# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from typing import Literal
from uuid import UUID

import pytest
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from pydantic import BaseModel
from pydantic import Field

from mora.mapping import OwnerInferencePriority


class ConfiguredBase(BaseModel):
    class Config:
        allow_mutation = False
        frozen = True
        allow_population_by_field_name = True
        use_enum_values = True


class Validity(ConfiguredBase):
    from_date: str = Field("1930-01-01", alias="from")
    to_date: str | None = Field(None, alias="to")


class Person(ConfiguredBase):
    uuid: UUID


class OrgUnitRef(ConfiguredBase):
    uuid: UUID


class Owner(ConfiguredBase):
    type: Literal["owner"] = "owner"
    uuid: UUID | None = None
    owner: Person | None = None
    org_unit: OrgUnitRef | None = None
    person: Person | None = None
    owner_inference_priority: OwnerInferencePriority | None = None
    validity: Validity


func_uuid = UUID("64181ed2-f1de-4c4a-a8fd-ab358c2c565b")

person1 = UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a")  # just some guy
person2 = UUID("236e0a78-11a0-4ed9-8545-6286bb8611c7")  # erik hansen (lots of data)
person3 = UUID("6ee24785-ee9a-4502-81c2-7697009c9053")  # just some guy

top_level_ou = UUID("2874e1dc-85e6-4269-823a-e1125484dfd3")
level2_ou = UUID("85715fc7-925d-401b-822d-467eb4b163b6")


def simplified_owner(
    uuid: UUID | None = None,
    owner: UUID | None = None,
    org_unit: UUID | None = None,
    person: UUID | None = None,
    owner_inference_priority: OwnerInferencePriority | None = None,
) -> dict[str, Any]:
    """
    human-friendly helper function: creates an owner object, either as the
    model object, or directly as json-friendly dict

    :param uuid:
    :param owner:
    :param org_unit:
    :param person:
    :return:
    """
    owner = Owner(
        uuid=uuid,
        owner=Person(uuid=owner) if owner else None,
        org_unit=OrgUnitRef(uuid=org_unit) if org_unit else None,
        person=Person(uuid=person) if person else None,
        owner_inference_priority=owner_inference_priority,
        validity=Validity(
            from_date="2017-01-01",
            to_date=None,
        ),
    )
    return jsonable_encoder(owner, by_alias=True)


@pytest.mark.integration_test
@pytest.mark.freeze_time("2017-01-01", tz_offset=1)
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "payload, status_code",
    [
        # Non existing
        # Need valid person
        (
            simplified_owner(
                uuid=func_uuid,
                owner=UUID("64181ed2-f1de-4c4a-a8fd-ab358c2c767b"),  # ANY value
                person=person1,
            ),
            404,
        ),
        # No owner
        # It should be possible to create "vacant" owners, i.e. valid person,
        # but simply no owner / vacant owner seat
        (
            simplified_owner(
                uuid=func_uuid,
                person=person1,
            ),
            201,
        ),
        # Create valid
        # Simply set both owner and person to valid objects
        (
            simplified_owner(
                uuid=func_uuid,
                owner=person2,
                person=person1,
            ),
            201,
        ),
        # With interference and owner
        # Cannot infer and have an owner
        (
            simplified_owner(
                uuid=func_uuid,
                owner=person2,
                person=person1,
                owner_inference_priority=OwnerInferencePriority.engagement,
            ),
            400,
        ),
    ],
)
def test_create_person(
    service_client: TestClient,
    payload: dict[str, Any],
    status_code: int,
) -> None:
    response = service_client.request(
        "POST", "/service/details/create", json=jsonable_encoder(payload)
    )
    assert response.status_code == status_code
