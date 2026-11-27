# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import uuid
from datetime import datetime
from typing import Any

from more_itertools import first

from .. import common
from .. import exceptions
from .. import lora
from .. import mapping
from .. import util
from ..triggers import Trigger
from . import handlers
from . import org
from .validation import validator


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

        await validator.is_date_range_in_org_unit_range(org_unit, valid_from, valid_to)
        await validator.is_date_range_in_org_unit_range(
            related_org_unit, valid_from, valid_to
        )

        func_id = util.get_uuid(req, required=False) or str(uuid.uuid4())
        await _ensure_not_already_related(
            org_unit_uuid, related_org_unit_uuid, valid_from, valid_to, func_id
        )
        bvn = util.checked_get(req, mapping.USER_KEY, "") or await _default_user_key(
            org_unit_uuid, related_org_unit_uuid, valid_from
        )

        payload = common.create_organisationsfunktion_payload(
            funktionsnavn=mapping.RELATED_UNIT_KEY,
            valid_from=valid_from,
            valid_to=valid_to,
            brugervendtnoegle=bvn,
            tilknyttedebrugere=[],
            tilknyttedeorganisationer=[org_uuid],
            tilknyttedeenheder=[org_unit_uuid, related_org_unit_uuid],
        )
        tag_related_units(payload, org_unit_uuid, related_org_unit_uuid)

        self.payload = payload
        self.uuid = func_id
        self.trigger_dict.update({Trigger.ORG_UNIT_UUID: org_unit_uuid})

    async def prepare_edit(self, req: dict[Any, Any]):
        related_unit_uuid = util.get_uuid(req)
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
        original = await c.organisationfunktion.get(uuid=related_unit_uuid)
        if not original:
            exceptions.ErrorCodes.E_NOT_FOUND(uuid=related_unit_uuid)

        data = req.get("data", {})
        new_from, new_to = util.get_validities(data)

        payload = {"note": "Rediger relateret enhed"}

        update_fields: list[tuple[mapping.FieldTuple, dict]] = [
            (mapping.ORG_FUNK_GYLDIGHED_FIELD, {"gyldighed": "Aktiv"})
        ]

        if mapping.USER_KEY in data:
            try:
                attributes = mapping.ORG_FUNK_EGENSKABER_FIELD(original)[-1].copy()
            except (TypeError, LookupError):  # pragma: no cover
                attributes = {}
            update_fields.append(
                (
                    mapping.ORG_FUNK_EGENSKABER_FIELD,
                    {
                        **attributes,
                        "brugervendtnoegle": util.checked_get(
                            data, mapping.USER_KEY, ""
                        ),
                    },
                )
            )

        # The units of a related unit never change, as a relation between other
        # units is another relation. The update may still extend the relation,
        # so the units must exist and not be related otherwise meanwhile.
        org_unit_uuid, related_org_unit_uuid = mapping.get_related_unit_uuids(original)
        assert org_unit_uuid is not None and related_org_unit_uuid is not None
        for unit_uuid in (org_unit_uuid, related_org_unit_uuid):
            await validator.is_date_range_in_org_unit_range(
                {mapping.UUID: unit_uuid}, new_from, new_to
            )
        await _ensure_not_already_related(
            org_unit_uuid, related_org_unit_uuid, new_from, new_to, related_unit_uuid
        )

        payload = common.update_payload(
            new_from, new_to, update_fields, original, payload
        )

        self.payload = payload
        self.uuid = related_unit_uuid
        self.trigger_dict.update({Trigger.ORG_UNIT_UUID: org_unit_uuid})


async def _ensure_not_already_related(
    org_unit_uuid: str,
    related_org_unit_uuid: str,
    valid_from: datetime,
    valid_to: datetime,
    related_unit_uuid: str,
) -> None:
    """Ensure no other related unit relates the units during the validity.

    Integrations using `related_units_update` (GraphQL version 30 and older)
    assume that a pair of units is related at most once.
    """
    c = lora.Connector(
        virkningfra=util.to_lora_time(valid_from),
        virkningtil=util.to_lora_time(valid_to),
    )
    others = await c.organisationfunktion.get_all(
        funktionsnavn=mapping.RELATED_UNIT_KEY,
        tilknyttedeenheder=org_unit_uuid,
        gyldighed="Aktiv",
    )
    for other_uuid, other in others:
        if other_uuid == related_unit_uuid:
            continue
        if related_org_unit_uuid in mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuids(other):
            exceptions.ErrorCodes.V_DUPLICATED_RELATED_UNIT(
                org_unit_uuid=org_unit_uuid,
                related_org_unit_uuid=related_org_unit_uuid,
                related_unit_uuid=other_uuid,
            )


async def _default_user_key(
    org_unit_uuid: str, related_org_unit_uuid: str, effective_date: datetime
) -> str:
    """Build a user-key from the user-keys of the related units."""
    c = lora.Connector(effective_date=effective_date)
    units = dict(
        await c.organisationenhed.get_all_by_uuid(
            uuids=[org_unit_uuid, related_org_unit_uuid]
        )
    )
    unit_bvn, related_unit_bvn = (
        first(mapping.ORG_UNIT_EGENSKABER_FIELD(units[u]))["brugervendtnoegle"]
        for u in (org_unit_uuid, related_org_unit_uuid)
    )
    return f"{unit_bvn} <-> {related_unit_bvn}"


def tag_related_units(
    payload: dict, org_unit_uuid: str, related_org_unit_uuid: str
) -> None:
    """Tag the units of a related unit payload with their roles.

    LoRa does not preserve the order of relations, so the order cannot be used
    to tell the units apart.
    """
    objekttypes = {
        org_unit_uuid: mapping.RELATED_UNIT_ORG_UNIT_OBJECTTYPE,
        related_org_unit_uuid: mapping.RELATED_UNIT_RELATED_ORG_UNIT_OBJECTTYPE,
    }
    for relation in mapping.ASSOCIATED_ORG_UNIT_FIELD(payload):
        relation["objekttype"] = objekttypes[relation["uuid"]]
