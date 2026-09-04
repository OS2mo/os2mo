# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from asyncio import create_task
from asyncio import gather
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from .. import common
from .. import exceptions
from .. import lora
from .. import mapping
from .. import util
from .models import RelatedUnitsUpdate


async def update_related_units(input: RelatedUnitsUpdate) -> UUID:
    """Updates relations for an org_unit."""
    input_dict = jsonable_encoder(input.to_handler_dict())

    origin = input_dict.pop("origin")
    handler = await _map_org_units(origin=origin, req=input_dict)
    if handler:
        uuid = origin

    return UUID(uuid)


# TODO: this was inlined from the service API as part of #71423, it's old code
#   but it has worked for years. It could benefit from being inlined further
#   because there is an unnecessary round-trip to a JSON dict and back
async def _map_org_units(origin: UUID | str, req: dict) -> dict[str, list[UUID | str]]:
    """Mark the given organisational units as related.

    Please note that this defines the related/mapped units for the
    given unit from the given timestamp and onwards. Any other
    preexisting mappings are terminated.

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
