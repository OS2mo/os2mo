# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional
from typing import Union
from uuid import UUID

import freezegun
import pytest
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from pydantic import Field
from tests.legacy.cases import AsyncConfigTestCase
from tests.legacy.cases import ConfigTestCase
from tests.legacy.util import load_fixture

from mora.mapping import OwnerInferencePriority


class ConfiguredBase(BaseModel):
    class Config:
        allow_mutation = False
        frozen = True
        allow_population_by_field_name = True
        use_enum_values = True


class Validity(ConfiguredBase):
    from_date: str = Field("1930-01-01", alias="from")
    to_date: Optional[str] = Field(None, alias="to")


class Person(ConfiguredBase):
    uuid: UUID


class OrgUnitRef(ConfiguredBase):
    uuid: UUID


class MoObj(ConfiguredBase):
    pass


class Owner(MoObj):
    type: Literal["owner"] = "owner"
    uuid: Optional[UUID] = None
    owner: Optional[Person] = None
    org_unit: Optional[OrgUnitRef] = None
    person: Optional[Person] = None
    owner_inference_priority: Optional[OwnerInferencePriority] = None
    validity: Validity


mock_uuid = ""

func_uuid = UUID("64181ed2-f1de-4c4a-a8fd-ab358c2c565b")

person1 = UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a")  # just some guy
person2 = UUID("236e0a78-11a0-4ed9-8545-6286bb8611c7")  # erik hansen (lots of data)
person3 = UUID("6ee24785-ee9a-4502-81c2-7697009c9053")  # just some guy
person4 = UUID("7626ad64-327d-481f-8b32-36c78eb12f8c")  # just some guy

top_level_ou = UUID("2874e1dc-85e6-4269-823a-e1125484dfd3")
level1_ou = UUID("9d07123e-47ac-4a9a-88c8-da82e3a4bc9e")
level2_ou = UUID("85715fc7-925d-401b-822d-467eb4b163b6")


def uuid_to_str(obj: Any):
    pass


#     """
#     recursive transforms UUID to str
#
#     :param obj: Anything, but most usefully a dict or UUID
#     :return: str if obj is UUID, otherwise the same type as original
#     """
#     if isinstance(obj, dict):
#         return {key: uuid_to_str(value) for key, value in obj.items()}
#     elif isinstance(obj, list):
#         return list(map(uuid_to_str, obj))
#     elif isinstance(obj, UUID):
#         return str(obj)
#
#     return obj


def simplified_owner(
    uuid: Optional[UUID] = None,
    owner: Optional[UUID] = None,
    org_unit: Optional[UUID] = None,
    person: Optional[UUID] = None,
    owner_inference_priority: Optional[OwnerInferencePriority] = None,
    from_date: str = "2017-01-01",
    to_date: Optional[str] = None,
    as_json: bool = True,
) -> Union[Owner, Dict[str, Any]]:
    """
    human-friendly helper function: creates an owner object, either as the
    model object, or directly as json-friendly dict

    :param uuid:
    :param owner:
    :param org_unit:
    :param person:
    :param from_date:
    :param to_date:
    :param as_json:
    :return:
    """
    owner = Owner(
        uuid=uuid,
        owner=Person(uuid=owner) if owner else None,
        org_unit=OrgUnitRef(uuid=org_unit) if org_unit else None,
        person=Person(uuid=person) if person else None,
        owner_inference_priority=owner_inference_priority,
        validity=Validity(
            from_date=from_date,
            to_date=to_date,
        ),
    )
    if as_json:
        return jsonable_encoder(owner, by_alias=True)
    return owner


@pytest.mark.usefixtures("sample_structures")
class OwnerOrgUnitTestCase(ConfigTestCase):
    def create_helper(
        self,
        jsonified_owner: Dict[str, Any],
        create_status_code: int,
        verifying_org_unit: UUID = top_level_ou,
        verifying_response: Optional[List[Dict[str, Any]]] = None,
    ):
        """

        :param jsonified_owner: Ready-to-send dict; Containing create-payload
        :param create_status_code: expected status code of create-operation
        :param verifying_org_unit: Target for verification, only used with response
        :param verifying_response: If success is expected, the returned value
        :return:
        """
        self.assertRequest(
            "/service/details/create",
            json=jsonified_owner,
            status_code=create_status_code,
        )

        # verify
        if verifying_response:
            self.assertRequestResponse(
                f"service/ou/{verifying_org_unit}/details/"
                f"owner?validity=present&at=2017-01-01&inherit_owner=1",
                jsonable_encoder(verifying_response),
            )


class BaseTests(OwnerOrgUnitTestCase):
    maxDiff = None

    def test_create_no_person_and_no_ou(self):
        """
        only partially filled; fail
        :return:
        """
        self.create_helper(
            jsonified_owner=simplified_owner(uuid=func_uuid, owner=person1),
            create_status_code=400,
        )

    def test_create_owner_non_existing(self):
        """
        if owner if set, it needs to be a valid person
        :return:
        """
        self.create_helper(
            jsonified_owner=simplified_owner(
                uuid=func_uuid,
                owner=UUID("64181ed2-f1de-4c4a-a8fd-ab358c2c767b"),  # ANY value
                org_unit=top_level_ou,
            ),
            create_status_code=404,
        )


@freezegun.freeze_time("2017-01-01", tz_offset=1)
class OrgUnitCreateTests(OwnerOrgUnitTestCase):
    maxDiff = None

    def test_create_ou_non_existing(self):
        """
        need valid ou
        :return:
        """
        self.create_helper(
            jsonified_owner=simplified_owner(
                uuid=func_uuid,
                owner=person1,
                org_unit=UUID("64181ed2-f1de-4c4a-a8fd-ab358c2c767b"),  # ANY value
            ),
            create_status_code=404,
        )

    def test_create_no_owner(self):
        """
        should be possible to create vacant owner
        :return:
        """
        self.create_helper(
            jsonified_owner=simplified_owner(uuid=func_uuid, org_unit=top_level_ou),
            create_status_code=201,
            verifying_response=[
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
        )

    def test_create_valid(self):
        """
        it should be possible to create "vacant" owners, i.e. valid org_unit, but simply
        no owner / vacant owner seat
        :return:
        """

        self.create_helper(
            jsonified_owner=simplified_owner(
                uuid=func_uuid,
                owner=person1,
                org_unit=top_level_ou,
                from_date="2017-01-01",
            ),
            create_status_code=201,
            verifying_response=[
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
        )

    def test_create_with_inference_priority(self):
        """
        inference priority is only relevant when dealing with person-person owners, so
        this should always fail
        :return:
        """
        self.create_helper(
            jsonified_owner=simplified_owner(
                uuid=func_uuid,
                owner=person1,
                org_unit=top_level_ou,
                owner_inference_priority=OwnerInferencePriority.engagement,
                from_date="2017-01-01",
            ),
            create_status_code=400,
        )


@pytest.mark.usefixtures("sample_structures")
@freezegun.freeze_time("2017-01-01", tz_offset=1)
class OrgUnitInheritTests(OwnerOrgUnitTestCase):
    maxDiff = None

    def test_inherit(self):
        """
        when absolutely no owner-orgfunc exists, inherit via the org hierarchy
        :return:
        """
        # attempt successful create, verify via child org-unit
        self.create_helper(
            jsonified_owner=simplified_owner(
                uuid=func_uuid,
                owner=person1,
                org_unit=top_level_ou,
                from_date="2017-01-01",
            ),
            create_status_code=201,
            verifying_org_unit=level2_ou,
            verifying_response=[
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
        )

    def test_inherit_top_level_empty(self):
        """
        when hitting top-level simply return nothing
        :return:
        """
        self.assertRequestResponse(
            f"service/ou/{level2_ou}/details/"
            f"owner?validity=present&at=2017-01-01&inherit_owner=1",
            [],
        )


@pytest.mark.usefixtures("sample_structures")
class AsyncOwnerPersonTestCase(AsyncConfigTestCase):
    async def create_helper(
        self,
        jsonified_owner: Dict[str, Any],
        create_status_code: int,
        verifying_person: UUID = person1,
        verifying_response: Optional[List[Dict[str, Any]]] = None,
    ):
        """

        :param jsonified_owner: Ready-to-send dict; Containing create-payload
        :param create_status_code: expected status code of create-operation
        :param verifying_org_unit: Target for verification, only used with response
        :param verifying_response: If success is expected, the returned value
        :return:
        """
        await self.assertRequest(
            "/service/details/create",
            json=jsonified_owner,
            status_code=create_status_code,
        )

        # verify
        if verifying_response:
            await self.assertRequestResponse(
                f"service/e/{verifying_person}/details/"
                f"owner?validity=present&at=2017-01-01&inherit_owner=1",
                verifying_response,
            )


@pytest.mark.usefixtures("sample_structures")
class OwnerPersonTestCase(ConfigTestCase):
    def create_helper(
        self,
        jsonified_owner: Dict[str, Any],
        create_status_code: int,
        verifying_person: UUID = person1,
        verifying_response: Optional[List[Dict[str, Any]]] = None,
    ):
        """

        :param jsonified_owner: Ready-to-send dict; Containing create-payload
        :param create_status_code: expected status code of create-operation
        :param verifying_org_unit: Target for verification, only used with response
        :param verifying_response: If success is expected, the returned value
        :return:
        """
        self.assertRequest(
            "/service/details/create",
            json=jsonified_owner,
            status_code=create_status_code,
        )

        # verify
        if verifying_response:
            self.assertRequestResponse(
                f"service/e/{verifying_person}/details/"
                f"owner?validity=present&at=2017-01-01&inherit_owner=1",
                verifying_response,
            )


@freezegun.freeze_time("2017-01-01", tz_offset=1)
class PersonTests(OwnerPersonTestCase):
    maxDiff = None

    def test_create_person_non_existing(self):
        """
        need valid person
        :return:
        """
        self.create_helper(
            jsonified_owner=simplified_owner(
                uuid=func_uuid,
                owner=UUID("64181ed2-f1de-4c4a-a8fd-ab358c2c767b"),  # ANY value
                person=person1,
            ),
            create_status_code=404,
        )

    def test_create_no_owner(self):
        """
        it should be possible to create "vacant" owners, i.e. valid person, but simply
        no owner / vacant owner seat
        :return:
        """
        self.create_helper(
            jsonified_owner=simplified_owner(
                uuid=func_uuid,
                person=person1,
            ),
            create_status_code=201,
            verifying_response=[],
        )

    def test_create_valid(self):
        """
        simply set both owner and person to valid objects
        :return:
        """
        self.create_helper(
            jsonified_owner=simplified_owner(
                uuid=func_uuid,
                owner=person2,
                person=person1,
            ),
            create_status_code=201,
            verifying_response=[],
        )

    def test_create_with_inference_and_owner(self):
        """
        cannot infer and have an owner
        :return:
        """
        self.create_helper(
            jsonified_owner=simplified_owner(
                uuid=func_uuid,
                owner=person2,
                person=person1,
                owner_inference_priority=OwnerInferencePriority.engagement,
            ),
            create_status_code=400,
            verifying_response=[],
        )


@pytest.mark.usefixtures("sample_structures")
class AsyncOwnerPersonTestInheritCase(AsyncOwnerPersonTestCase):
    async def asyncSetUp(self):
        """
        Load a bunch of data so we have something to inherit.
        Particularly, we need both engagements and associations
        :return:
        """
        await super().asyncSetUp()

        await load_fixture(
            "organisation/organisationfunktion",
            "create_organisationfunktion_tilknytning_eriksmidthansen.json",
        )
        await load_fixture(
            "organisation/organisationfunktion",
            "create_organisationfunktion_tilknytning_eriksmidthansen_sekundaer.json",
        )
        await self.setup_org_units()

    async def setup_org_units(self):
        """
        set some owners, so we have something to inherit
        :return:
        """
        # create owner in org_unit so we have something to inherit
        await self.assertRequest(
            "/service/details/create",
            json=simplified_owner(
                owner=person1,
                org_unit=top_level_ou,
                from_date="2017-01-01",
            ),
            status_code=201,
        )

        # create owner in level2 org_unit so we can distinguish from top_level
        await self.assertRequest(
            "/service/details/create",
            json=simplified_owner(
                owner=person3,
                org_unit=level2_ou,
                from_date="2017-01-01",
            ),
            status_code=201,
        )

    async def create_helper(
        self,
        jsonified_owner: Dict[str, Any],
        create_status_code: int,
        verifying_response: Optional[List[Dict[str, Any]]] = None,
    ):
        """

        :param jsonified_owner: Ready-to-send dict; Containing create-payload
        :param create_status_code: expected status code of create-operation
        :param verifying_response: If success is expected, the returned value
        :return:
        """

        await self.assertRequest(
            "/service/details/create",
            json=jsonified_owner,
            status_code=create_status_code,
        )

        # verify
        if verifying_response:
            await self.assertRequestResponse(
                f"service/e/{person2}/details/"
                f"owner?validity=present&at=2017-01-01&inherit_owner=1",
                verifying_response,
            )

    async def test_create_with_engagement_priority_and_engagement(self):
        """
        should follow engagement and find owner
        :return:
        """
        await self.create_helper(
            jsonified_owner=simplified_owner(
                uuid=func_uuid,
                person=person2,
                owner_inference_priority=OwnerInferencePriority.engagement,
            ),
            create_status_code=201,
            verifying_response=[
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
        )

    async def test_create_with_association_priority_and_multiple_associations(self):
        """
        should follow association with highest priority
        :return:
        """
        await self.create_helper(
            jsonified_owner=simplified_owner(
                uuid=func_uuid,
                person=person2,
                owner_inference_priority=OwnerInferencePriority.association,
            ),
            create_status_code=201,
            verifying_response=[
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
        )


@pytest.mark.usefixtures("sample_structures")
@freezegun.freeze_time("2018-01-01", tz_offset=1)
class OwnerEditCase(OwnerPersonTestCase):
    def setUp(self):
        """
        Load a bunch of data so we have something to inherit.
        Particularly, we need both engagements and associations
        :return:
        """
        super().setUp()

        # create owner in org_unit so we have something to inherit / edit
        self.assertRequest(
            "/service/details/create",
            json=simplified_owner(
                owner=person1,
                org_unit=top_level_ou,
                from_date="2017-01-01",
            ),
            status_code=201,
        )

        # create owner in level2 org_unit so we can distinguish from top_level
        self.assertRequest(
            "/service/details/create",
            json=simplified_owner(
                owner=person3,
                org_unit=level2_ou,
                from_date="2017-01-01",
            ),
            status_code=201,
        )

        # create owner in person so we have something to edit
        self.assertRequest(
            "/service/details/create",
            json=simplified_owner(
                uuid=func_uuid,
                person=person2,
                owner_inference_priority=OwnerInferencePriority.engagement,
            ),
            status_code=201,
        )

    def edit_helper(
        self,
        jsonified_owner: Dict[str, Any],
        edit_status_code: int,
        verifying_type: str,
        verifying_obj_uuid: UUID,
        verifying_response: Optional[List[Dict[str, Any]]] = None,
    ):
        """

        :param jsonified_owner: Ready-to-send dict; Containing create-payload
        :param edit_status_code: expected status code of edit-operation
        :param verifying_type: enum: "e" / "ou"
        :param verifying_obj_uuid: uuid of the "thing" to check after edit
        :param verifying_response: If success is expected, the returned value
        :return:
        """

        self.assertRequest(
            "/service/details/edit",
            json=jsonified_owner,
            status_code=edit_status_code,
        )

        # verify
        if verifying_response:
            self.assertRequestResponse(
                f"service/{verifying_type}/{verifying_obj_uuid}/details/"
                f"owner?validity=present&at=2017-01-01&inherit_owner=1",
                verifying_response,
            )

    def terminate_helper(
        self,
        terminate_func_uuid: UUID,
        end_date: str,
        terminate_status_code: int,
        verifying_type: str,
        verifying_obj_uuid: UUID,
        verifying_response: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        :param terminate_func_uuid: uuid of func to terminate
        :param end_date: date to terminate at
        :param terminate_status_code: expected status code of edit-operation
        :param verifying_type: enum: "e" / "ou"
        :param verifying_obj_uuid: uuid of the "thing" to check after edit
        :param verifying_response: If success is expected, the returned value
        :return:
        """

        self.assertRequest(
            "/service/details/edit",
            json={
                "type": "owner",
                "uuid": str(terminate_func_uuid),
                "validity": {"to": end_date},
            },
            status_code=terminate_status_code,
        )

        # verify
        if verifying_response:
            self.assertRequestResponse(
                f"service/{verifying_type}/{verifying_obj_uuid}/details/"
                f"owner?validity=present&at=2017-01-01&inherit_owner=1",
                verifying_response,
            )

    def edit_person(self):
        """
        edit between valid person formats
        :return:
        """
        # from inferred to person
        self.edit_helper(
            jsonified_owner=simplified_owner(
                uuid=func_uuid,
                person=person2,
                owner=person3,
            ),
            edit_status_code=201,
            verifying_type="e",
            verifying_obj_uuid=person2,
            verifying_response=[{}],
        )
        # from person to another person
        self.edit_helper(
            jsonified_owner=simplified_owner(
                uuid=func_uuid,
                person=person2,
                owner=person4,
            ),
            edit_status_code=201,
            verifying_type="e",
            verifying_obj_uuid=person2,
            verifying_response=[{}],
        )
        # from person to vacant
        self.edit_helper(
            jsonified_owner=simplified_owner(
                uuid=func_uuid,
                person=person2,
            ),
            edit_status_code=201,
            verifying_type="e",
            verifying_obj_uuid=person2,
            verifying_response=[{}],
        )
        # from vacant back to inferred
        self.edit_helper(
            jsonified_owner=simplified_owner(
                uuid=func_uuid,
                person=person2,
                owner_inference_priority=OwnerInferencePriority.engagement,
            ),
            edit_status_code=201,
            verifying_type="e",
            verifying_obj_uuid=person2,
            verifying_response=[{}],
        )

        # terminate
        self.terminate_helper(
            terminate_func_uuid=func_uuid,
            end_date="2017-02-01",
            terminate_status_code=200,
            verifying_type="e",
            verifying_obj_uuid=person2,
            verifying_response=[],
        )

    def edit_ou(self):
        """
        edit between valid ou states
        :return:
        """
        # from person to person
        self.edit_helper(
            jsonified_owner=simplified_owner(
                uuid=func_uuid,
                org_unit=level2_ou,
                owner=person2,
            ),
            edit_status_code=201,
            verifying_type="ou",
            verifying_obj_uuid=level2_ou,
            verifying_response=[{}],
        )

        # from person to vacant
        self.edit_helper(
            jsonified_owner=simplified_owner(
                uuid=func_uuid,
                person=person2,
            ),
            edit_status_code=201,
            verifying_type="ou",
            verifying_obj_uuid=level2_ou,
            verifying_response=[{}],
        )

        # terminate
        self.terminate_helper(
            terminate_func_uuid=func_uuid,
            end_date="2017-02-01",
            terminate_status_code=200,
            verifying_type="ou",
            verifying_obj_uuid=level2_ou,
            verifying_response=[],
        )
