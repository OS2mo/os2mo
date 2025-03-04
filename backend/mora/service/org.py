# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""
Organisation
------------

This section describes how to interact with organisations.
"""

from fastapi import APIRouter
from more_itertools import one

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
        async def get_lora_organisation(c, orgid, org=None):
            if not org:  # pragma: no cover
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

        c = common.lora.Connector(virkningfra="-infinity", virkningtil="infinity")
        orgs = list(await c.organisation.get_all(bvn="%"))

        if len(orgs) > 1:
            exceptions.ErrorCodes.E_ORG_TOO_MANY(count=len(orgs))

        elif len(orgs) == 0:
            exceptions.ErrorCodes.E_ORG_UNCONFIGURED()

        orgid, org = one(orgs)
        cls.organisation = await get_lora_organisation(c, orgid, org)
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

    if uuid and uuid != org["uuid"]:  # pragma: no cover
        exceptions.ErrorCodes.E_ORG_NOT_ALLOWED(uuid=uuid)

    return org
