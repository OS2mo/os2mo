# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""
IT Systems
----------

This section describes how to interact with IT systems.

"""

from operator import itemgetter
from typing import TYPE_CHECKING
from typing import Any
from uuid import uuid4

from fastapi import APIRouter
from structlog import get_logger

from .. import common
from .. import exceptions
from .. import lora
from .. import mapping
from .. import util
from ..service.facet import get_mo_object_primary_value
from ..service.facet import is_class_uuid_primary
from ..triggers import Trigger
from . import handlers
from . import org
from .validation import validator
from .validation.models import GroupValidation

if TYPE_CHECKING:  # pragma: no cover
    from ..handler.reading import ReadingHandler


router = APIRouter()

logger = get_logger()

MO_OBJ_TYPE = dict[str, Any]


class _ITUserGroupValidation(GroupValidation):
    @classmethod
    async def get_validation_items_from_mo_object(cls, mo_object: dict) -> list[dict]:
        return [
            {
                "uuid": util.get_uuid(mo_object, required=False),
                "employee_uuid": util.get_mapping_uuid(mo_object, mapping.PERSON),
                "it_system_uuid": util.get_mapping_uuid(mo_object, mapping.ITSYSTEM),
                "engagement_uuids": tuple(
                    util.checked_get(mo_object, mapping.ENGAGEMENTS, [], required=False)
                ),
                "it_user_username": mo_object.get(mapping.USER_KEY),
                "is_primary": await get_mo_object_primary_value(mo_object),
            }
        ]

    @classmethod
    def get_mo_object_reading_handler(cls) -> "ReadingHandler":
        # Avoid circular import
        from ..handler.impl.it import ItSystemBindingReader

        return ItSystemBindingReader()


class ITUserUniqueGroupValidation(_ITUserGroupValidation):
    def validate(self) -> None:
        self.validate_unique_constraint(
            [
                "employee_uuid",
                "it_system_uuid",
                "it_user_username",
                "engagement_uuids",
            ],
            exceptions.ErrorCodes.V_DUPLICATED_IT_USER,
        )


class ITUserPrimaryGroupValidation(_ITUserGroupValidation):
    def validate(self) -> None:
        self.validate_at_most_one(
            itemgetter("it_system_uuid"),
            itemgetter("is_primary"),
            exceptions.ErrorCodes.V_MORE_THAN_ONE_PRIMARY,
        )


class ItsystemRequestHandler(handlers.OrgFunkRequestHandler):
    role_type = mapping.IT
    function_key = mapping.ITSYSTEM_KEY
    group_validations: list[GroupValidation] = [
        ITUserUniqueGroupValidation,
        ITUserPrimaryGroupValidation,
    ]

    async def prepare_create(self, req):
        c = lora.Connector()

        systemid = util.get_mapping_uuid(req, mapping.ITSYSTEM, required=True)
        system = await c.itsystem.get(systemid)
        note = req.get(mapping.NOTE)

        if not system:
            exceptions.ErrorCodes.E_NOT_FOUND()

        org_unit = util.checked_get(req, mapping.ORG_UNIT, {}, required=False)
        org_unit_uuid = util.get_uuid(org_unit, required=False)

        employee = util.checked_get(req, mapping.PERSON, {}, required=False)
        employee_uuid = util.get_uuid(employee, required=False)

        engagement = util.checked_get(req, mapping.ENGAGEMENT, {}, required=False)
        engagements = util.checked_get(req, mapping.ENGAGEMENTS, [], required=False)

        # Ensure backwards compatibility with the deprecated single engagement
        # uuid.
        if engagement and engagements:  # pragma: no cover
            exceptions.ErrorCodes.E_INVALID_INPUT(
                "Attempted use of both 'engagement' and 'engagements'"
            )
        if engagement:
            engagements = [engagement]
        engagement_uuids = [util.get_uuid(e) for e in engagements]

        org_uuid = (
            await org.get_configured_organisation(
                util.get_mapping_uuid(req, mapping.ORG, required=False)
            )
        )["uuid"]

        valid_from, valid_to = util.get_validities(req)

        func_id = util.get_uuid(req, required=False) or str(uuid4())
        bvn = util.checked_get(req, mapping.USER_KEY, func_id)

        primary = util.get_mapping_uuid(req, mapping.PRIMARY, required=False)

        # Validation
        if org_unit:  # pragma: no cover
            await validator.is_date_range_in_org_unit_range(
                org_unit, valid_from, valid_to
            )

        if employee:
            await validator.is_date_range_in_employee_range(
                employee, valid_from, valid_to
            )

        if employee_uuid and systemid:
            validation = await ITUserUniqueGroupValidation.from_mo_objects(
                dict(
                    tilknyttedebrugere=employee_uuid,
                    tilknyttedeitsystemer=systemid,
                )
            )
            validation.add_validation_item(
                dict(
                    employee_uuid=employee_uuid,
                    it_system_uuid=systemid,
                    it_user_username=bvn,
                    engagement_uuids=tuple(engagement_uuids),
                )
            ).validate()

        if (
            employee_uuid and systemid and (await is_class_uuid_primary(primary))
        ):  # pragma: no cover
            validation = await ITUserPrimaryGroupValidation.from_mo_objects(
                dict(tilknyttedebrugere=employee_uuid),
            )
            validation.add_validation_item(
                dict(
                    employee_uuid=employee_uuid,
                    it_system_uuid=systemid,
                    is_primary=True,
                ),
            ).validate()

        # TODO: validate that the date range is in
        # the validity of the IT system!

        external_id = req.get(mapping.EXTERNAL_ID)

        func = common.create_organisationsfunktion_payload(
            funktionsnavn=mapping.ITSYSTEM_KEY,
            primær=primary,
            valid_from=valid_from,
            valid_to=valid_to,
            brugervendtnoegle=bvn,
            tilknyttedebrugere=[employee_uuid] if employee_uuid else [],
            tilknyttedeorganisationer=[org_uuid],
            tilknyttedeenheder=[org_unit_uuid] if org_unit_uuid else [],
            tilknyttedeitsystemer=[systemid],
            tilknyttedefunktioner=[
                common.associated_orgfunc(
                    uuid=engagement_uuid, orgfunc_type=mapping.MoOrgFunk.ENGAGEMENT
                )
                for engagement_uuid in engagement_uuids
            ],
            udvidelse_attributter={mapping.EXTENSION_1: external_id}
            if external_id is not None
            else None,
            note=note,
        )

        self.payload = func
        self.uuid = func_id
        self.trigger_dict.update(
            {Trigger.EMPLOYEE_UUID: employee_uuid, Trigger.ORG_UNIT_UUID: org_unit_uuid}
        )

    async def prepare_edit(self, req: dict):
        function_uuid = util.get_uuid(req)

        # Get the current org-funktion which the user wants to change
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
        original = await c.organisationfunktion.get(uuid=function_uuid)

        if not original:
            exceptions.ErrorCodes.E_NOT_FOUND()

        data = req.get("data")
        new_from, new_to = util.get_validities(data)

        payload = {
            "note": data.get(mapping.NOTE, "Rediger IT-system"),
        }

        original_data = req.get("original")
        if original_data:  # pragma: no cover
            # We are performing an update
            old_from, old_to = util.get_validities(original_data)
            payload = common.inactivate_old_interval(
                old_from,
                old_to,
                new_from,
                new_to,
                payload,
                ("tilstande", "organisationfunktiongyldighed"),
            )

        update_fields = [
            # Always update gyldighed
            (mapping.ORG_FUNK_GYLDIGHED_FIELD, {"gyldighed": "Aktiv"}),
        ]

        if mapping.ITSYSTEM in data:
            update_fields.append(
                (
                    mapping.SINGLE_ITSYSTEM_FIELD,
                    {"uuid": util.get_mapping_uuid(data, mapping.ITSYSTEM)},
                )
            )

        if data.get(mapping.PERSON):  # pragma: no cover
            update_fields.append(
                (
                    mapping.USER_FIELD,
                    {
                        "uuid": util.get_mapping_uuid(data, mapping.PERSON),
                    },
                )
            )

        if (
            mapping.ENGAGEMENT in data and mapping.ENGAGEMENTS in data
        ):  # pragma: no cover
            exceptions.ErrorCodes.E_INVALID_INPUT(
                "Attempted use of both 'engagement' and 'engagements'"
            )
        if (engagements := data.get(mapping.ENGAGEMENTS)) is not None or data.get(
            mapping.ENGAGEMENT
        ):
            if engagements is None:
                engagements = [data.get(mapping.ENGAGEMENT)]
            if not engagements:  # pragma: no cover
                # If an empty list is returned it is registered as a relation to a function with no uuid
                # This is how we "delete" a list of engagements
                update_fields.append(
                    (mapping.ASSOCIATED_FUNCTION_FIELD, {"uuid": "", "urn": ""})
                )
            else:
                for engagement in engagements:
                    update_fields.append(
                        (
                            mapping.ASSOCIATED_FUNCTION_FIELD,
                            {
                                "uuid": engagement["uuid"],
                                mapping.OBJECTTYPE: mapping.ENGAGEMENT,
                            },
                        )
                    )

        if data.get(mapping.ORG_UNIT):
            update_fields.append(
                (
                    mapping.ASSOCIATED_ORG_UNIT_FIELD,
                    {
                        "uuid": util.get_mapping_uuid(data, mapping.ORG_UNIT),
                    },
                )
            )

        if data.get(mapping.PRIMARY):  # pragma: no cover
            update_fields.append(
                (
                    mapping.PRIMARY_FIELD,
                    {
                        "uuid": util.get_mapping_uuid(data, mapping.PRIMARY),
                    },
                )
            )

        if mapping.EXTERNAL_ID in data:  # pragma: no cover
            update_fields.append(
                (
                    mapping.ORG_FUNK_UDVIDELSER_FIELD,
                    {mapping.EXTENSION_1: data.get(mapping.EXTERNAL_ID)},
                )
            )

        try:
            attributes = mapping.ORG_FUNK_EGENSKABER_FIELD(original)[-1].copy()
        except (TypeError, LookupError):  # pragma: no cover
            attributes = {}
        new_attributes = {}

        if mapping.USER_KEY in data:  # pragma: no cover
            new_attributes["brugervendtnoegle"] = util.checked_get(
                data, mapping.USER_KEY, ""
            )

        if new_attributes:  # pragma: no cover
            update_fields.append(
                (
                    mapping.ORG_FUNK_EGENSKABER_FIELD,
                    {**attributes, **new_attributes},
                )
            )

        # Validation prerequisites
        systemid = util.get_mapping_uuid(data, mapping.ITSYSTEM, required=False)
        employee_uuid = util.get_mapping_uuid(data, mapping.PERSON, required=False)

        engagement_uuids = tuple(
            mapping.ASSOCIATED_FUNCTION_FIELD.get_uuids(engagements)
        )
        primary = util.get_mapping_uuid(data, mapping.PRIMARY, required=False)
        bvn = util.checked_get(data, mapping.USER_KEY, default="", required=False)

        # Validation
        if (
            employee_uuid and systemid and (await is_class_uuid_primary(primary))
        ):  # pragma: no cover
            validation = await ITUserPrimaryGroupValidation.from_mo_objects(
                dict(tilknyttedebrugere=employee_uuid),
            )
            validation.update_validation_item(
                function_uuid,
                dict(
                    employee_uuid=employee_uuid,
                    it_system_uuid=systemid,
                    is_primary=True,
                ),
            ).validate()

        if employee_uuid and systemid and bvn:  # pragma: no cover
            validation = await ITUserUniqueGroupValidation.from_mo_objects(
                dict(
                    tilknyttedebrugere=employee_uuid,
                    tilknyttedeitsystemer=systemid,
                )
            )
            validation.update_validation_item(
                function_uuid,
                dict(
                    employee_uuid=employee_uuid,
                    it_system_uuid=systemid,
                    it_user_username=bvn,
                    engagement_uuids=engagement_uuids,
                ),
            ).validate()

        payload = common.update_payload(
            new_from, new_to, update_fields, original, payload
        )

        bounds_fields = list(
            mapping.ITSYSTEM_FIELDS.difference(
                {x[0] for x in update_fields},
            )
        )
        payload = common.ensure_bounds(
            new_from, new_to, bounds_fields, original, payload
        )

        self.payload = payload
        self.uuid = function_uuid
        self.trigger_dict.update(
            {
                Trigger.ORG_UNIT_UUID: (
                    mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(original)
                ),
                Trigger.EMPLOYEE_UUID: (
                    util.get_mapping_uuid(data, mapping.PERSON)
                    or mapping.USER_FIELD.get_uuid(original)
                ),
            }
        )
