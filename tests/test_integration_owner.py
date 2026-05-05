# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from typing import Literal
from uuid import UUID

import freezegun
import pytest
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from mora.mapping import OwnerInferencePriority
from pydantic import BaseModel
from pydantic import Field

from tests.util import load_fixture


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
@pytest.mark.usefixtures("fixture_db")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
def test_inherit_top_level_empty(service_client: TestClient) -> None:
    """When hitting top-level simply return nothing."""
    response = service_client.request(
        "GET",
        f"service/ou/{level2_ou}/details/owner",
        params={"validity": "present", "at": "2017-01-01", "inherit_owner": 1},
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "payload, status_code, verifying_org_unit, verifying_response",
    [
        # Inherit
        # When absolutely no owner-orgfunc exists, inherit via the org hierarchy
        # Attempt successful create, verify via child org-unit
        (
            simplified_owner(
                uuid=func_uuid,
                owner=person1,
                org_unit=top_level_ou,
            ),
            201,
            level2_ou,
            [
                {
                    "org_unit": {
                        "name": "Overordnet Enhed",
                        "user_key": "root",
                        "uuid": top_level_ou,
                        "validity": {"from": "2016-01-01", "to": None},
                    },
                    "owner": {
                        "givenname": "Anders",
                        "name": "Anders And",
                        "nickname": "Donald Duck",
                        "nickname_givenname": "Donald",
                        "nickname_surname": "Duck",
                        "seniority": None,
                        "surname": "And",
                        "uuid": person1,
                    },
                    "person": None,
                    "owner_inference_priority": None,
                    "user_key": "64181ed2-f1de-4c4a-a8fd-ab358c2c565b",
                    "uuid": func_uuid,
                    "validity": {"from": "2017-01-01", "to": None},
                }
            ],
        ),
        # Non existing
        # Need valid OU
        (
            simplified_owner(
                uuid=func_uuid,
                owner=person1,
                org_unit=UUID("64181ed2-f1de-4c4a-a8fd-ab358c2c767b"),  # ANY value
            ),
            404,
            None,
            None,
        ),
        # No owner
        (
            simplified_owner(uuid=func_uuid, org_unit=top_level_ou),
            201,
            None,
            [
                {
                    "org_unit": {
                        "name": "Overordnet Enhed",
                        "user_key": "root",
                        "uuid": top_level_ou,
                        "validity": {"from": "2016-01-01", "to": None},
                    },
                    "owner": None,
                    "owner_inference_priority": None,
                    "person": None,
                    "user_key": "64181ed2-f1de-4c4a-a8fd-ab358c2c565b",
                    "uuid": func_uuid,
                    "validity": {"from": "2017-01-01", "to": None},
                }
            ],
        ),
        # Valid
        # It should be possible to create "vacant" owners, i.e. valid org_unit
        # But simply no owner / vacant owner seat
        (
            simplified_owner(
                uuid=func_uuid,
                owner=person1,
                org_unit=top_level_ou,
            ),
            201,
            None,
            [
                {
                    "org_unit": {
                        "name": "Overordnet Enhed",
                        "user_key": "root",
                        "uuid": top_level_ou,
                        "validity": {"from": "2016-01-01", "to": None},
                    },
                    "owner": {
                        "givenname": "Anders",
                        "name": "Anders And",
                        "nickname": "Donald Duck",
                        "nickname_givenname": "Donald",
                        "nickname_surname": "Duck",
                        "seniority": None,
                        "surname": "And",
                        "uuid": person1,
                    },
                    "person": None,
                    "owner_inference_priority": None,
                    "user_key": "64181ed2-f1de-4c4a-a8fd-ab358c2c565b",
                    "uuid": func_uuid,
                    "validity": {"from": "2017-01-01", "to": None},
                }
            ],
        ),
        # Interference priority
        # Inference priority is only relevant when dealing with person-person owners,
        # so this should always fail
        (
            simplified_owner(
                uuid=func_uuid,
                owner=person1,
                org_unit=top_level_ou,
                owner_inference_priority=OwnerInferencePriority.engagement,
            ),
            400,
            None,
            None,
        ),
        # No person and no ou
        # Only partically filled => fail
        (
            simplified_owner(uuid=func_uuid, owner=person1),
            400,
            None,
            None,
        ),
        # Owner non existing
        (
            simplified_owner(
                uuid=func_uuid,
                owner=UUID("64181ed2-f1de-4c4a-a8fd-ab358c2c767b"),  # ANY value
                org_unit=top_level_ou,
            ),
            404,
            None,
            None,
        ),
    ],
)
@freezegun.freeze_time("2017-01-01", tz_offset=1)
def test_create_org_unit(
    service_client: TestClient,
    payload: dict[str, Any],
    status_code: int,
    verifying_org_unit: UUID | None,
    verifying_response: dict[str, None] | None,
) -> None:
    response = service_client.request(
        "POST", "/service/details/create", json=jsonable_encoder(payload)
    )
    assert response.status_code == status_code

    # verify
    if verifying_response is not None:
        verifying_org_unit = verifying_org_unit or top_level_ou
        response = service_client.request(
            "GET",
            f"service/ou/{verifying_org_unit}/details/owner",
            params={"validity": "present", "at": "2017-01-01", "inherit_owner": 1},
        )
        assert response.status_code == 200
        assert response.json() == jsonable_encoder(verifying_response)


@pytest.mark.integration_test
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
@freezegun.freeze_time("2017-01-01", tz_offset=1)
def test_create_person(
    service_client: TestClient,
    payload: dict[str, Any],
    status_code: int,
) -> None:
    response = service_client.request(
        "POST", "/service/details/create", json=jsonable_encoder(payload)
    )
    assert response.status_code == status_code


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "payload, status_code, verifying_response",
    [
        # Engagement with priority and engagement
        # Should follow engagement and find owner
        (
            simplified_owner(
                uuid=func_uuid,
                person=person2,
                owner_inference_priority=OwnerInferencePriority.engagement,
            ),
            201,
            [
                {
                    "org_unit": None,
                    "owner": {
                        "givenname": "Anders",
                        "name": "Anders And",
                        "nickname": "Donald Duck",
                        "nickname_givenname": "Donald",
                        "nickname_surname": "Duck",
                        "seniority": None,
                        "surname": "And",
                        "uuid": str(person1),
                    },
                    "owner_inference_priority": "engagement_priority",
                    "person": {
                        "givenname": "Erik Smidt",
                        "name": "Erik Smidt Hansen",
                        "nickname": "",
                        "nickname_givenname": "",
                        "nickname_surname": "",
                        "seniority": None,
                        "surname": "Hansen",
                        "uuid": str(person2),
                    },
                    "user_key": "64181ed2-f1de-4c4a-a8fd-ab358c2c565b",
                    "uuid": "64181ed2-f1de-4c4a-a8fd-ab358c2c565b",
                    "validity": {"from": "2017-01-01", "to": None},
                }
            ],
        ),
        # Association with priorty and multiple associations
        # Should follow association with highest priority
        (
            simplified_owner(
                uuid=func_uuid,
                person=person2,
                owner_inference_priority=OwnerInferencePriority.association,
            ),
            201,
            [
                {
                    "org_unit": None,
                    "owner": {
                        "givenname": "Fedtmule",
                        "name": "Fedtmule Hund",
                        "nickname": "George Geef",
                        "nickname_givenname": "George",
                        "nickname_surname": "Geef",
                        "seniority": None,
                        "surname": "Hund",
                        "uuid": str(person3),
                    },
                    "owner_inference_priority": "association_priority",
                    "person": {
                        "givenname": "Erik Smidt",
                        "name": "Erik Smidt Hansen",
                        "nickname": "",
                        "nickname_givenname": "",
                        "nickname_surname": "",
                        "seniority": None,
                        "surname": "Hansen",
                        "uuid": str(person2),
                    },
                    "user_key": "64181ed2-f1de-4c4a-a8fd-ab358c2c565b",
                    "uuid": "64181ed2-f1de-4c4a-a8fd-ab358c2c565b",
                    "validity": {"from": "2017-01-01", "to": None},
                }
            ],
        ),
    ],
)
@freezegun.freeze_time("2017-01-01", tz_offset=1)
async def test_create_person_extended(
    another_transaction,
    service_client: TestClient,
    payload: dict[str, Any],
    status_code: int,
    verifying_response: dict[str, None] | None,
) -> None:
    async with another_transaction():
        # Load a bunch of data so we have something to inherit.
        # Particularly, we need both engagements and associations
        await load_fixture(
            "organisation/organisationfunktion",
            "create_organisationfunktion_tilknytning_eriksmidthansen.json",
        )
        await load_fixture(
            "organisation/organisationfunktion",
            "create_organisationfunktion_tilknytning_eriksmidthansen_sekundaer.json",
        )

    # Set some owners, so we have something to inherit
    # create owner in org_unit so we have something to inherit
    response = service_client.request(
        "POST",
        "/service/details/create",
        json=simplified_owner(
            owner=person1,
            org_unit=top_level_ou,
        ),
    )
    assert response.status_code == 201

    # create owner in level2 org_unit so we can distinguish from top_level
    response = service_client.request(
        "POST",
        "/service/details/create",
        json=simplified_owner(
            owner=person3,
            org_unit=level2_ou,
        ),
    )
    assert response.status_code == 201

    response = service_client.request(
        "POST", "/service/details/create", json=jsonable_encoder(payload)
    )
    assert response.status_code == status_code

    # verify
    if verifying_response is not None:
        response = service_client.request(
            "GET",
            f"service/e/{person2}/details/owner",
            params={"validity": "present", "at": "2017-01-01", "inherit_owner": 1},
        )
        assert response.status_code == 200
        assert response.json() == jsonable_encoder(verifying_response)
