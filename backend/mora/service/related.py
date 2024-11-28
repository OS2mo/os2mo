# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""
Related Units
-------------

This section describes how to interact with related units.

"""
from asyncio import create_task
from asyncio import gather
from uuid import UUID

from fastapi import APIRouter
from fastapi import Body

from . import handlers
from .. import common
from .. import exceptions
from .. import lora
from .. import mapping
from .. import util

router = APIRouter()


class RelatedUnitRequestHandler(handlers.OrgFunkRequestHandler):
    """This is a dummy handler that exists to enable reading related units.

    Eventually, we'll do that in the handlers, but for now we use
    their _existence_ to allow reading.

    """

    role_type = "related_unit"
    function_key = mapping.RELATED_UNIT_KEY

    def prepare_create(self, req: dict):
        raise NotImplementedError

    def prepare_edit(self, req: dict):
        raise NotImplementedError


@router.post("/ou/{origin}/map")
async def map_org_units(origin: UUID, req: dict = Body(...)):
    print("#################")
    print(req)
    """Mark the given organisational units as related.

    .. :quickref: Unit; Map

    Please note that this defines the related/mapped units for the
    given unit from the given timestamp and onwards. Any other
    preexisting mappings are terminated.

    :statuscode 200: The operation succeeded.
    :statuscode 404: No such unit found.
    :statuscode 409: Validation failed, see below.

    :param origin: The UUID of the organisational unit.

    :<json Array destination: The UUIDs of other units to map the unit to.
    :<json str validity.from: The date on which the termination should happen,
        in ISO 8601.

    :>json Array added: The UUIDs of added function relations.
    :>json Array removed: The UUIDs of removed function relations.
    :>json Array unchanged: The UUIDs of function relations not modified.

    **Example Request**:

    .. sourcecode:: json

      {
          "destination": [
              "04c78fc2-72d2-4d02-b55f-807af19eac48",
              "469d655b-6d61-446a-90f0-989448f08654"
          ],
          "validity": {
              "from": "2017-03-01"
          }
      }

    **Example Response**:

    .. sourcecode:: json

      {
          "added": [
              "9ec1eab4-abcc-432c-899d-86dce18d4fa2"
          ],
          "deleted": [
              "daa77a4d-6500-483d-b099-2c2eb7fa7a76"
          ],
          "unchanged": [
              "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
          ]
      }

    **Validation**:

    All of the given organisation units must exist at the given date,
    and they must not be terminated.

    """
    origin = str(origin)

    from_date = util.get_valid_from(req)
    to_date = util.get_valid_to(req)

    c = lora.Connector(effective_date=from_date)
    destinations = set(util.checked_get(req, "destination", [], required=True))
    if origin in destinations:
        exceptions.ErrorCodes.E_RELATED_TO_SELF(
            origin=origin,
            destinations=sorted(destinations),
        )

    wanted_units = {origin} | destinations
    units = dict(await c.organisationenhed.get_all_by_uuid(uuids=sorted(wanted_units)))

    if len(units) != len(wanted_units):
        exceptions.ErrorCodes.E_ORG_UNIT_NOT_FOUND(
            org_unit_uuid=sorted(wanted_units - units.keys()),
        )

    units_start = max(
        util.get_effect_from(state)
        for unitid, unit in units.items()
        for state in util.get_states(unit)
        if state["gyldighed"] == "Aktiv"
    )
    units_end = min(
        util.get_effect_to(state)
        for unitid, unit in units.items()
        for state in util.get_states(unit)
        if state["gyldighed"] == "Aktiv"
    )
    print(units_start)
    print(units_end)
    print(from_date)
    print(to_date)
    if units_end < units_start or from_date < units_start or to_date > units_end:
        exceptions.ErrorCodes.V_VALIDITIES_DO_NOT_OVERLAP(
            origin=origin,
            destinations=destinations,
            from_date=from_date,
            to_date=to_date,
        )

    (orgid,) = mapping.BELONGS_TO_FIELD.get_uuids(units[origin])

    preexisting = {
        unitid: funcid
        for funcid, func in await c.organisationfunktion.get_all(
            funktionsnavn=mapping.RELATED_UNIT_KEY,
            tilknyttedeenheder=origin,
            gyldighed="Aktiv",
        )
        for unitid in mapping.ASSOCIATED_ORG_UNITS_FIELD.get_uuids(func)
        if unitid != origin
    }
    print("preexisting", preexisting)

    edits = {
        funcid: common.inactivate_org_funktion_payload(
            from_date,
            "Fjern relateret organisation",
        )
        for unitid, funcid in preexisting.items()
        if unitid not in destinations
    }
    print("edits", edits)

    if edits and not to_date == util.POSITIVE_INFINITY:
        print("Hurra")
        exceptions.ErrorCodes.E_RELATED_UNITS_EDIT_WITH_TO_DATE(
            origin=origin, to_date=to_date, destinations=destinations
        )

    creations = [
        common.create_organisationsfunktion_payload(
            mapping.RELATED_UNIT_KEY,
            from_date,
            to_date,
            "{} <-> {}".format(
                mapping.ORG_UNIT_EGENSKABER_FIELD(units[origin])[0][
                    "brugervendtnoegle"
                ],
                mapping.ORG_UNIT_EGENSKABER_FIELD(units[destid])[0][
                    "brugervendtnoegle"
                ],
            ),
            tilknyttedebrugere=[],
            tilknyttedeorganisationer=[orgid],
            tilknyttedeenheder=[origin, destid],
        )
        for destid in destinations
        if destid not in preexisting
    ]

    return {
        "deleted": sorted(
            await gather(
                *[
                    create_task(c.organisationfunktion.update(req, funcid))
                    for funcid, req in edits.items()
                ]
            )
        ),
        "added": sorted(
            await gather(
                *[create_task(c.organisationfunktion.create(req)) for req in creations]
            )
        ),
        "unchanged": sorted(destinations & preexisting.keys()),
    }
