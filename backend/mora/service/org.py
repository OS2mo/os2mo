# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

"""
Organisation
------------

This section describes how to interact with organisations.
"""

from asyncio import create_task, gather
from uuid import UUID

from fastapi import APIRouter

from .. import common
from .. import exceptions
from .. import mapping
from .. import util
from ..exceptions import ErrorCodes

router = APIRouter()


class ConfiguredOrganisation:
    """OS2mo organisation is cached as an attribute on this class
    hence there must be exactly one organisation in the lora database
    """
    organisation = None
    valid = False

    @classmethod
    async def validate(cls):
        orglist = await get_valid_organisations()

        if len(orglist) > 1:
            exceptions.ErrorCodes.E_ORG_TOO_MANY(count=len(orglist))

        elif len(orglist) == 0:
            exceptions.ErrorCodes.E_ORG_UNCONFIGURED()

        elif len(orglist) == 1:
            cls.organisation = orglist[0]
            cls.valid = True

    @classmethod
    def clear(cls):
        cls.organisation = None
        cls.valid = False


async def get_configured_organisation(uuid=None):
    if not ConfiguredOrganisation.valid:
        await ConfiguredOrganisation.validate()
    org = ConfiguredOrganisation.organisation

    if uuid and uuid != org["uuid"]:
        exceptions.ErrorCodes.E_ORG_NOT_ALLOWED(uuid=uuid)

    return org


async def get_lora_organisation(c, orgid, org=None):
    if not org:
        org = await c.organisation.get(orgid)

        if not org or not util.is_reg_valid(org):
            return None

    attrs = org["attributter"]["organisationegenskaber"][0]
    ret = {
        "name": attrs["organisationsnavn"],
        "user_key": attrs["brugervendtnoegle"],
        "uuid": orgid,
    }
    return ret


async def get_valid_organisations():
    """return all valid organisations, being the ones
    who have at least one top organisational unit
    """
    c = common.lora.Connector(virkningfra="-infinity", virkningtil="infinity")
    orgs = await c.organisation.get_all(bvn="%")
    orglist = await gather(
        *[create_task(get_lora_organisation(c, orgid, org)) for orgid, org in orgs]
    )
    return orglist


@router.get("/o/")
# @util.restrictargs('at')
async def list_organisations():
    """List displayable organisations. This endpoint is retained for
    backwards compatibility. It will always return a list of only one
    organisation as only one organisation is currently allowed.

    .. :quickref: Organisation; List

    :queryparam date at: Show organisations at this point in time,
        in ISO-8601 format. This parameter is retained for backwards
        compatibility. There can be only one organisation defined
        at any point in time

    :<jsonarr string name: Human-readable name of the organisation.
    :<jsonarr string user_key: Short, unique key identifying the unit.
    :<jsonarr string uuid: Machine-friendly UUID of the organisation.

    :status 200: Always.

    **Example Response**:

    .. sourcecode:: json

     [
       {
         "name": "Hj\u00f8rring Kommune",
         "user_key": "Hj\u00f8rring Kommune",
         "uuid": "8d79e880-02cf-46ed-bc13-b5f73e478575"
       }
     ]

    """
    return [await get_configured_organisation()]


@router.get("/o/{orgid}/")
# @util.restrictargs('at')
async def get_organisation(orgid: UUID):
    """
    Obtain the initial level of an organisation.

    .. :quickref: Organisation; Getter

    :queryparam date at: Show the organisation at this point in time,
        in ISO-8601 format.

    :<json string name: Human-readable name of the organisation.
    :<json string user_key: Short, unique key identifying the unit.
    :<json string uuid: Machine-friendly UUID of the organisation.
    :<json int child_count: Number of org. units nested immediately beneath
                            the organisation.
    :<json int person_count: Amount of people belonging to this organisation.
    :<json int unit_count: Amount of units belonging to this organisation.
    :<json int employment_count: Amount of employments in this organisation.
    :<json int association_count: Amount of associations in this organisation.
    :<json int leave_count: Amount of leaves in this organisation.
    :<json int role_count: Amount of roles in this organisation.
    :<json int manager_count: Amount of managers in this organisation.

    :status 200: Whenever the organisation exists and is readable.
    :status 404: When no such organisation exists.

    **Example Response**:

    .. sourcecode:: json

     {
       "association_count": 24,
       "child_count": 2,
       "engagement_count": 111,
       "leave_count": 0,
       "manager_count": 41,
       "name": "Hj\u00f8rring Kommune",
       "person_count": 132,
       "role_count": 22,
       "unit_count": 67,
       "user_key": "Hj\u00f8rring Kommune",
       "uuid": "8d79e880-02cf-46ed-bc13-b5f73e478575"
     }

    """
    orgid = str(orgid)
    c = common.get_connector()
    org = await c.organisation.get(orgid)

    try:
        attrs = org["attributter"]["organisationegenskaber"][0]
    except (KeyError, TypeError):
        ErrorCodes.E_NO_SUCH_ENDPOINT()

    units = await c.organisationenhed.fetch(tilhoerer=orgid, gyldighed="Aktiv")
    children = await c.organisationenhed.fetch(overordnet=orgid, gyldighed="Aktiv")

    # FIXME: we should filter for activity, but that's extremely slow
    # 0.8s -> 12.3s for 28k users and 33k functions
    # https://redmine.magenta-aps.dk/issues/21273
    users = await c.bruger.fetch(tilhoerer=orgid)
    engagements = await c.organisationfunktion.fetch(
        tilknyttedeorganisationer=orgid, funktionsnavn=mapping.ENGAGEMENT_KEY
    )

    associations = await c.organisationfunktion.fetch(
        tilknyttedeorganisationer=orgid,
        funktionsnavn=mapping.ASSOCIATION_KEY,
    )
    leaves = await c.organisationfunktion.fetch(
        tilknyttedeorganisationer=orgid, funktionsnavn=mapping.LEAVE_KEY
    )
    roles = await c.organisationfunktion.fetch(
        tilknyttedeorganisationer=orgid, funktionsnavn=mapping.ROLE_KEY
    )
    managers = await c.organisationfunktion.fetch(
        tilknyttedeorganisationer=orgid, funktionsnavn=mapping.MANAGER_KEY
    )

    ret = {
        "name": attrs["organisationsnavn"],
        "user_key": attrs["brugervendtnoegle"],
        "uuid": orgid,
        "child_count": len(children),
        "unit_count": len(units),
        "person_count": len(users),
        "engagement_count": len(engagements),
        "association_count": len(associations),
        "leave_count": len(leaves),
        "role_count": len(roles),
        "manager_count": len(managers),
    }
    return ret
