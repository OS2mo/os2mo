# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""
Related Units
-------------

This section describes how to interact with related units.

"""

import uuid
from asyncio import create_task
from asyncio import gather
from typing import Any
from uuid import UUID

from fastapi import APIRouter
from fastapi import Body

from .. import common
from .. import exceptions
from .. import lora
from .. import mapping
from .. import util
from . import handlers
from . import org

router = APIRouter()


class RelatedUnitRequestHandler(handlers.OrgFunkRequestHandler):
    role_type = "related_unit"
    function_key = mapping.RELATED_UNIT_KEY

    async def prepare_create(self, req: dict[Any, Any]):
        org_unit = util.checked_get(req, mapping.ORG_UNIT, {}, required=True)
        org_unit_uuid = util.get_uuid(org_unit, required=True)

        related_org_unit = util.checked_get(req, "related_org_unit", {}, required=True)
        related_org_unit_uuid = util.get_uuid(related_org_unit, required=True)

        if org_unit_uuid == related_org_unit_uuid:
            exceptions.ErrorCodes.E_RELATED_TO_SELF(
                origin=org_unit_uuid,
                destinations=[related_org_unit_uuid],
            )

        org_ = await org.get_configured_organisation(
            util.get_mapping_uuid(req, mapping.ORG, required=False)
        )
        org_uuid = org_["uuid"]

        valid_from, valid_to = util.get_validities(req)

        func_id = util.get_uuid(req, required=False) or str(uuid.uuid4())
        bvn = util.checked_get(req, mapping.USER_KEY, func_id)

        # If user_key was not provided (defaults to func_id), build from unit names
        if bvn == func_id:
            c = lora.Connector(effective_date=valid_from)
            units = dict(
                await c.organisationenhed.get_all_by_uuid(
                    uuids=[org_unit_uuid, related_org_unit_uuid]
                )
            )
            if org_unit_uuid in units and related_org_unit_uuid in units:
                unit1_bvn = mapping.ORG_UNIT_EGENSKABER_FIELD(units[org_unit_uuid])[0][
                    "brugervendtnoegle"
                ]
                unit2_bvn = mapping.ORG_UNIT_EGENSKABER_FIELD(
                    units[related_org_unit_uuid]
                )[0]["brugervendtnoegle"]
                bvn = f"{unit1_bvn} <-> {unit2_bvn}"

        payload = common.create_organisationsfunktion_payload(
            funktionsnavn=mapping.RELATED_UNIT_KEY,
            valid_from=valid_from,
            valid_to=valid_to,
            brugervendtnoegle=bvn,
            tilknyttedebrugere=[],
            tilknyttedeorganisationer=[org_uuid],
            tilknyttedeenheder=[org_unit_uuid, related_org_unit_uuid],
        )

        self.payload = payload
        self.uuid = func_id
        self.trigger_dict.update(
            {
                "org_unit_uuid": org_unit_uuid,
            }
        )

    async def prepare_edit(self, req: dict[Any, Any]):
        related_unit_uuid = req.get("uuid")
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
        original = await c.organisationfunktion.get(uuid=related_unit_uuid)

        data = req.get("data", {})
        new_from, new_to = util.get_validities(data)

        payload = {"note": "Rediger relateret enhed"}

        original_data = req.get("original")
        if original_data:  # pragma: no cover
            old_from, old_to = util.get_validities(original_data)
            payload = common.inactivate_old_interval(
                old_from,
                old_to,
                new_from,
                new_to,
                payload,
                ("tilstande", "organisationfunktiongyldighed"),
            )

        update_fields = []

        # Always update gyldighed
        update_fields.append((mapping.ORG_FUNK_GYLDIGHED_FIELD, {"gyldighed": "Aktiv"}))

        try:
            attributes = mapping.ORG_FUNK_EGENSKABER_FIELD(original)[-1].copy()
        except (TypeError, LookupError):  # pragma: no cover
            attributes = {}
        new_attributes = {}

        if mapping.USER_KEY in data:
            new_attributes["brugervendtnoegle"] = util.checked_get(
                data, mapping.USER_KEY, ""
            )

        if new_attributes:
            update_fields.append(
                (
                    mapping.ORG_FUNK_EGENSKABER_FIELD,
                    {**attributes, **new_attributes},
                )
            )

        # Update org units if provided
        org_unit_uuid = util.get_mapping_uuid(data, mapping.ORG_UNIT)
        related_org_unit_uuid = util.get_mapping_uuid(data, "related_org_unit")

        if org_unit_uuid or related_org_unit_uuid:
            # Get current org units from original
            current_org_units = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuids(original)
            current_org_unit = (
                current_org_units[0] if len(current_org_units) > 0 else None
            )
            current_related = (
                current_org_units[1] if len(current_org_units) > 1 else None
            )

            new_org_unit = org_unit_uuid or current_org_unit
            new_related = related_org_unit_uuid or current_related

            if new_org_unit == new_related:
                exceptions.ErrorCodes.E_RELATED_TO_SELF(
                    origin=new_org_unit,
                    destinations=[new_related],
                )

            # We need to update the entire tilknyttedeenheder list
            update_fields.append(
                (mapping.ASSOCIATED_ORG_UNIT_FIELD, {"uuid": new_org_unit})
            )

        payload = common.update_payload(
            new_from, new_to, update_fields, original, payload
        )

        self.payload = payload
        self.uuid = related_unit_uuid
        self.trigger_dict.update(
            {
                "org_unit_uuid": org_unit_uuid
                or mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(original),
            }
        )


@router.post("/ou/{origin}/map")
async def map_org_units(origin: UUID, req: dict = Body(...)):
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

    date = util.get_valid_from(req)
    c = lora.Connector(effective_date=date)
    destinations = set(util.checked_get(req, "destination", [], required=True))
    if origin in destinations:  # pragma: no cover
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

    good = {
        unitid
        for unitid, unit in units.items()
        for state in util.get_states(unit)
        if util.get_effect_to(state) == util.POSITIVE_INFINITY
        and state["gyldighed"] == "Aktiv"
    }

    if wanted_units - good:
        exceptions.ErrorCodes.V_DATE_OUTSIDE_ORG_UNIT_RANGE(
            org_unit_uuid=sorted(wanted_units - good),
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

    edits = {
        funcid: common.inactivate_org_funktion_payload(
            date,
            "Fjern relateret organisation",
        )
        for unitid, funcid in preexisting.items()
        if unitid not in destinations
    }

    creations = [
        common.create_organisationsfunktion_payload(
            mapping.RELATED_UNIT_KEY,
            date,
            util.POSITIVE_INFINITY,
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
