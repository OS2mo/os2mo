# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
"""
Organisation
------------

This section describes how to interact with organisations.
"""
from asyncio import create_task
from asyncio import gather

from fastapi import APIRouter

from .. import common
from .. import exceptions
from .. import util


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
    # Access to validate() is guarded behind a lock to ensure we don't schedule multiple
    # (in some cases hundreds) requests on the very first call before the cache (the
    # 'organisation' attribute) is populated.
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
