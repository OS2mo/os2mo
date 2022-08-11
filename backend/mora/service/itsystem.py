# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
"""
IT Systems
----------

This section describes how to interact with IT systems.

"""
from operator import itemgetter
from typing import Any
from typing import Awaitable
from typing import Dict
from typing import List
from typing import Optional
from typing import TYPE_CHECKING
from uuid import uuid4

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from pydantic.decorator import validate_arguments
from ramodels.mo.details.it_system import ITUserWrite
from structlog import get_logger

from . import handlers
from . import org
from .. import common
from .. import exceptions
from .. import lora
from .. import mapping
from .. import util
from ..lora import LoraObjectType
from ..service.facet import get_mo_object_primary_value
from ..service.facet import is_class_uuid_primary
from ..triggers import Trigger
from .validation import validator
from .validation.models import GroupValidation
from mora.request_scoped.bulking import request_wide_bulk

if TYPE_CHECKING:  # pragma: no cover
    from ..handler.reading import ReadingHandler


router = APIRouter()

logger = get_logger()

MO_OBJ_TYPE = Dict[str, Any]


class _ITUserGroupValidation(GroupValidation):
    @classmethod
    async def get_validation_items_from_mo_object(cls, mo_object: dict) -> List[dict]:
        return [
            {
                "uuid": util.get_uuid(mo_object, required=False),
                "employee_uuid": util.get_mapping_uuid(mo_object, mapping.PERSON),
                "it_system_uuid": util.get_mapping_uuid(mo_object, mapping.ITSYSTEM),
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
            ["employee_uuid", "it_system_uuid", "it_user_username"],
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

    @validate_arguments
    async def prepare_create(self, req: ITUserWrite):
        req = jsonable_encoder(req.dict(by_alias=True))
        c = lora.Connector()

        systemid = util.get_mapping_uuid(req, mapping.ITSYSTEM, required=True)
        system = await c.itsystem.get(systemid)

        if not system:
            exceptions.ErrorCodes.E_NOT_FOUND()

        org_unit = util.checked_get(req, mapping.ORG_UNIT, {}, required=False)
        org_unit_uuid = util.get_uuid(org_unit, required=False)

        employee = util.checked_get(req, mapping.PERSON, {}, required=False)
        employee_uuid = util.get_uuid(employee, required=False)

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
        if org_unit:
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
                )
            ).validate()

        if employee_uuid and systemid and (await is_class_uuid_primary(primary)):
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
            "note": "Rediger IT-system",
        }

        original_data = req.get("original")
        if original_data:
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

        if data.get(mapping.PERSON):
            update_fields.append(
                (
                    mapping.USER_FIELD,
                    {
                        "uuid": util.get_mapping_uuid(data, mapping.PERSON),
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

        if data.get(mapping.PRIMARY):
            update_fields.append(
                (
                    mapping.PRIMARY_FIELD,
                    {
                        "uuid": util.get_mapping_uuid(data, mapping.PRIMARY),
                    },
                )
            )

        try:
            attributes = mapping.ORG_FUNK_EGENSKABER_FIELD(original)[-1].copy()
        except (TypeError, LookupError):
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

        # Validation prerequisites
        systemid = util.get_mapping_uuid(data, mapping.ITSYSTEM, required=False)
        employee_uuid = util.get_mapping_uuid(data, mapping.PERSON, required=False)
        primary = util.get_mapping_uuid(data, mapping.PRIMARY, required=False)
        bvn = util.checked_get(data, mapping.USER_KEY, default="", required=False)

        # Validation
        if employee_uuid and systemid and is_class_uuid_primary(primary):
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

        if employee_uuid and systemid and bvn:
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


async def __get_itsystem_from_cache(
    systemid: str, only_primary_uuid: bool = False
) -> MO_OBJ_TYPE:
    """
    Get org unit from cache and process it
    :param systemid: uuid of it-system
    :param only_primary_uuid:
    :return: A processed system
    """
    return await get_one_itsystem(
        c=request_wide_bulk.connector,
        systemid=systemid,
        system=await request_wide_bulk.get_lora_object(
            type_=LoraObjectType.it_system, uuid=systemid
        )
        if not only_primary_uuid
        else None,
        only_primary_uuid=only_primary_uuid,
    )


async def request_bulked_get_one_itsystem(
    systemid: str, only_primary_uuid: bool = False
) -> Awaitable[MO_OBJ_TYPE]:
    """
    EAGERLY adds a uuid to a LAZILY-processed cache. Return an awaitable. Once the
    result is awaited, the FULL cache is processed. Useful to 'under-the-hood' bulk.

    :param systemid: uuid of it-system
    :param only_primary_uuid:
    :return: Awaitable returning the processed system
    """
    return __get_itsystem_from_cache(
        systemid=systemid, only_primary_uuid=only_primary_uuid
    )


async def get_one_itsystem(
    c: lora.Connector, systemid, system=None, only_primary_uuid=False
) -> Optional[MO_OBJ_TYPE]:
    """Obtain the list of engagements corresponding to a user.

    .. :quickref: IT system; Get by user

    :queryparam date at: Current time in ISO-8601 format.
    :queryparam string validity: Only show *past*, *present* or
        *future* values -- which the default being to show *present*
        values.

    :param uuid id: The UUID to query, i.e. the ID of the employee or
        unit.

    All requests contain validity objects on the following form:

    :<jsonarr string from: The from date, in ISO 8601.
    :<jsonarr string to: The to date, in ISO 8601.

    .. sourcecode:: json

      {
        "from": "2016-01-01",
        "to": "2017-12-31",
      }

    :<jsonarr string name:
        The name of the IT system in question.
    :<jsonarr string user_key:
        Short, unique key identifying the IT-system in question.
    :<jsonarr string reference:
        Optional string describing the elements of the IT system.
    :<jsonarr string system_type:
        Optional string describing the system_type of the IT system.
    :<jsonarr string name:
        The name of the IT system in question.
    :<jsonarr string uuid: Machine-friendly UUID.
    :<jsonarr string validity: The validity times of the object.

    :status 200: Always.

    **Example response**:

    .. sourcecode:: json

      [
        {
          "name": "Lokal Rammearkitektur",
          "reference": null,
          "system_type": null,
          "user_key": "LoRa",
          "uuid": "0872fb72-926d-4c5c-a063-ff800b8ee697",
          "validity": {
            "from": "2016-01-01",
            "to": "2017-12-31"
          },
        },
        {
          "name": "Active Directory",
          "reference": null,
          "system_type": null,
          "user_key": "AD",
          "uuid": "59c135c9-2b15-41cc-97c8-b5dff7180beb",
          "validity": {
            "from": "2002-02-14",
            "to": null
          },
        }
      ]

    """

    if only_primary_uuid:
        return {mapping.UUID: systemid}

    if not system:
        system = await c.itsystem.get(systemid)

        if not system or not util.is_reg_valid(system):
            return None

    system_attrs = system["attributter"]["itsystemegenskaber"][0]

    return {
        "uuid": systemid,
        "name": system_attrs.get("itsystemnavn"),
        "reference": system_attrs.get("konfigurationreference"),
        "system_type": system_attrs.get("itsystemtype"),
        "user_key": system_attrs.get("brugervendtnoegle"),
        mapping.VALIDITY: util.get_effect_validity(
            system["tilstande"]["itsystemgyldighed"][0],
        ),
    }
