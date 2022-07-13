# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
"""
Associations
------------

This section describes how to interact with employee associations.

"""
import uuid
from operator import itemgetter
from typing import Any
from typing import Dict
from typing import List
from typing import TYPE_CHECKING

from more_itertools import one
from structlog import get_logger

from . import handlers
from . import org
from .. import common
from .. import conf_db
from .. import exceptions
from .. import lora
from .. import mapping
from .. import util
from ..handler.impl.association import AssociationReader
from ..service.facet import get_mo_object_primary_value
from ..service.facet import is_class_uuid_primary
from .validation import validator
from .validation.models import GroupValidation

if TYPE_CHECKING:  # pragma: no cover
    from ..handler.reading import ReadingHandler


logger = get_logger()


class _ITAssociationGroupValidation(GroupValidation):
    @classmethod
    async def get_validation_items_from_mo_object(cls, mo_object: dict) -> List[dict]:
        if mo_object is None:
            return []

        it_users = mo_object.get(mapping.IT) or []
        result = []

        for it_user in it_users:
            try:
                it_user_uuid = it_user[mapping.UUID]
                it_system_uuid = it_user[mapping.ITSYSTEM][mapping.UUID]
            except KeyError:
                continue  # not an "IT association", skip it
            else:
                item = {
                    "uuid": util.get_uuid(mo_object),
                    "employee_uuid": util.get_mapping_uuid(mo_object, mapping.PERSON),
                    "org_unit_uuid": util.get_mapping_uuid(mo_object, mapping.ORG_UNIT),
                    "it_user_uuid": it_user_uuid,
                    "it_system_uuid": it_system_uuid,
                    "is_primary": await get_mo_object_primary_value(mo_object),
                }
                result.append(item)

        return result

    @classmethod
    def get_mo_object_reading_handler(cls) -> "ReadingHandler":
        return AssociationReader()


class ITAssociationUniqueGroupValidation(_ITAssociationGroupValidation):
    def validate(self) -> None:
        self.validate_unique_constraint(
            ["employee_uuid", "org_unit_uuid", "it_user_uuid"],
            exceptions.ErrorCodes.V_MORE_THAN_ONE_ASSOCIATION,
        )


class ITAssociationPrimaryGroupValidation(_ITAssociationGroupValidation):
    def validate(self) -> None:
        self.validate_at_most_one(
            itemgetter("it_system_uuid"),
            itemgetter("is_primary"),
            exceptions.ErrorCodes.V_MORE_THAN_ONE_PRIMARY,
        )


class AssociationRequestHandler(handlers.OrgFunkRequestHandler):
    role_type = mapping.ASSOCIATION
    function_key = mapping.ASSOCIATION_KEY
    group_validations: list[GroupValidation] = [
        ITAssociationUniqueGroupValidation,
        ITAssociationPrimaryGroupValidation,
    ]

    @staticmethod
    def substitute_is_needed(association_type_uuid: str) -> bool:
        """
        checks whether the chosen association needs a substitute
        """
        substitute_roles: str = conf_db.get_configuration()[conf_db.SUBSTITUTE_ROLES]
        if substitute_roles == "":
            # no role need substitute
            return False

        if association_type_uuid in substitute_roles.split(","):
            # chosen role does need substitute
            return True
        else:
            return False

    async def prepare_create(self, req: Dict[Any, Any]):
        """
        To create a vacant association, set employee_uuid to None and set a
        value org_unit_uuid
        :param req: request as received by flask
        :return:
        """
        org_unit = util.checked_get(req, mapping.ORG_UNIT, {}, required=True)
        org_unit_uuid = util.get_uuid(org_unit, required=True)

        dynamic_classes = util.checked_get(req, mapping.CLASSES, [])
        dynamic_classes = list(map(util.get_uuid, dynamic_classes))

        employee = util.checked_get(req, mapping.PERSON, {})
        employee_uuid = util.get_uuid(employee, required=False)

        org_ = await org.get_configured_organisation(
            util.get_mapping_uuid(req, mapping.ORG, required=False)
        )
        org_uuid = org_["uuid"]

        valid_from, valid_to = util.get_validities(req)

        func_id = util.get_uuid(req, required=False) or str(uuid.uuid4())
        bvn = util.checked_get(req, mapping.USER_KEY, func_id)

        primary = util.get_mapping_uuid(req, mapping.PRIMARY)
        substitute_uuid = util.get_mapping_uuid(req, mapping.SUBSTITUTE)
        job_function_uuid = util.get_mapping_uuid(req, mapping.JOB_FUNCTION)
        it_user_uuid = util.get_mapping_uuid(req, mapping.IT)
        association_type_uuid = util.get_mapping_uuid(
            req, mapping.ASSOCIATION_TYPE, required=False if it_user_uuid else True
        )

        # Validation
        # remove substitute if not needed
        await validator.is_mutually_exclusive(substitute_uuid, job_function_uuid)
        if substitute_uuid and association_type_uuid:  # substitute is specified
            validator.is_substitute_allowed(association_type_uuid)
        await validator.is_date_range_in_org_unit_range(org_unit, valid_from, valid_to)
        if employee:
            await validator.is_date_range_in_employee_range(
                employee, valid_from, valid_to
            )
        if employee_uuid:
            validator.is_substitute_self(
                employee_uuid=employee_uuid, substitute_uuid=substitute_uuid
            )
        if employee_uuid and org_unit_uuid and it_user_uuid:
            validation = await ITAssociationUniqueGroupValidation.from_mo_objects(
                dict(
                    tilknyttedebrugere=employee_uuid,
                    tilknyttedeenheder=org_unit_uuid,
                ),
            )
            validation.add_validation_item(
                dict(
                    employee_uuid=employee_uuid,
                    org_unit_uuid=org_unit_uuid,
                    it_user_uuid=it_user_uuid,
                ),
            ).validate()
        if employee_uuid and it_user_uuid and (await is_class_uuid_primary(primary)):
            validation = await ITAssociationPrimaryGroupValidation.from_mo_objects(
                dict(tilknyttedebrugere=employee_uuid),
            )
            validation.add_validation_item(
                dict(
                    employee_uuid=employee_uuid,
                    it_user_uuid=it_user_uuid,
                    it_system_uuid=(await self._get_it_system_uuid(it_user_uuid)),
                    is_primary=True,
                ),
            ).validate()

        if substitute_uuid:
            rel_orgfunc_uuids = [substitute_uuid]
        elif job_function_uuid:
            rel_orgfunc_uuids = [job_function_uuid]
        else:
            rel_orgfunc_uuids = []

        payload_kwargs = dict(
            funktionsnavn=mapping.ASSOCIATION_KEY,
            primær=primary,
            valid_from=valid_from,
            valid_to=valid_to,
            brugervendtnoegle=bvn,
            tilknyttedebrugere=[employee_uuid],
            tilknyttedeorganisationer=[org_uuid],
            tilknyttedeenheder=[org_unit_uuid],
            tilknyttedeklasser=dynamic_classes,
            tilknyttedefunktioner=rel_orgfunc_uuids,
            tilknyttedeitsystemer=[it_user_uuid] if it_user_uuid else None,
            funktionstype=association_type_uuid,
        )

        association = common.create_organisationsfunktion_payload(**payload_kwargs)

        self.payload = association
        self.uuid = func_id
        self.trigger_dict.update(
            {
                "employee_uuid": employee_uuid,
                "org_unit_uuid": org_unit_uuid,
            }
        )

    async def prepare_edit(self, req: Dict[Any, Any]):
        """
        To edit into a vacant association, set employee_uuid to None and set a
        value org_unit_uuid
        :param req: request as received by flask
        :return:
        """
        association_uuid = req.get("uuid")
        # Get the current org-funktion which the user wants to change
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
        original = await c.organisationfunktion.get(uuid=association_uuid)

        data = req.get("data", {})
        new_from, new_to = util.get_validities(data)

        payload = dict()
        payload["note"] = "Rediger tilknytning"

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

        update_fields = list()

        # Always update gyldighed
        update_fields.append((mapping.ORG_FUNK_GYLDIGHED_FIELD, {"gyldighed": "Aktiv"}))

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

        # Update "job_function"
        job_function_uuid = util.get_mapping_uuid(data, mapping.JOB_FUNCTION)
        if job_function_uuid:
            # We store the job function in "tilknyttedefunktioner", so update that
            # field, rather than `mapping.JOB_FUNCTION_FIELD`, which points to "opgaver"
            update_fields.append(
                (mapping.ASSOCIATED_FUNCTION_FIELD, {"uuid": job_function_uuid})
            )

        # Update "it" (UUID of IT user, in case this association is an IT association)
        it_user_uuid = util.get_mapping_uuid(data, mapping.IT)
        if it_user_uuid:
            update_fields.append(
                (mapping.SINGLE_ITSYSTEM_FIELD, {"uuid": it_user_uuid})
            )

        # Update "association_type"
        association_type_uuid = util.get_mapping_uuid(data, mapping.ASSOCIATION_TYPE)
        if association_type_uuid:
            update_fields.append(
                (
                    mapping.ORG_FUNK_TYPE_FIELD,
                    {"uuid": association_type_uuid},
                )
            )
            if not util.is_substitute_allowed(association_type_uuid):
                # Updates "tilknyttedefunktioner"
                update_fields.append(
                    (mapping.ASSOCIATED_FUNCTION_FIELD, {"uuid": "", "urn": ""})
                )

        # Update org unit UUID
        if mapping.ORG_UNIT in data:
            org_unit_uuid = data.get(mapping.ORG_UNIT).get("uuid")
            update_fields.append(
                (
                    mapping.ASSOCIATED_ORG_UNIT_FIELD,
                    {"uuid": org_unit_uuid},
                )
            )
        else:
            org_unit_uuid = util.get_obj_uuid(
                original,
                mapping.ASSOCIATED_ORG_UNIT_FIELD.path,
            )

        # Update person UUID
        if mapping.PERSON in data:
            employee = data.get(mapping.PERSON, {})
            if employee:
                employee_uuid = employee.get("uuid")
                update_payload = {"uuid": employee_uuid}
            else:  # allow missing, e.g. vacant association
                employee_uuid = util.get_mapping_uuid(data, mapping.PERSON)
                update_payload = {"uuid": "", "urn": ""}
            update_fields.append((mapping.USER_FIELD, update_payload))
        else:
            employee = util.get_obj_value(original, mapping.USER_FIELD.path)[-1]
            employee_uuid = util.get_uuid(employee)

        # Update "substitute"
        if mapping.SUBSTITUTE in data and data.get(mapping.SUBSTITUTE):
            substitute = data.get(mapping.SUBSTITUTE)
            substitute_uuid = substitute.get("uuid")
            if employee_uuid:
                validator.is_substitute_self(
                    employee_uuid=employee_uuid, substitute_uuid=substitute_uuid
                )
            if not substitute_uuid:
                update_fields.append(
                    (mapping.ASSOCIATED_FUNCTION_FIELD, {"uuid": "", "urn": ""})
                )
            else:
                association_type_uuid = util.get_mapping_uuid(
                    data, mapping.ASSOCIATION_TYPE, required=True
                )
                validator.is_substitute_allowed(association_type_uuid)
                update_fields.append(
                    (mapping.ASSOCIATED_FUNCTION_FIELD, {"uuid": substitute_uuid})
                )

        # Update "primary"
        if mapping.PRIMARY in data and data.get(mapping.PRIMARY):
            primary = util.get_mapping_uuid(data, mapping.PRIMARY)
            update_fields.append((mapping.PRIMARY_FIELD, {"uuid": primary}))
        else:
            primary = None

        # Update "dynamic_classes"
        for clazz in util.checked_get(data, mapping.CLASSES, []):
            update_fields.append(
                (mapping.ORG_FUNK_CLASSES_FIELD, {"uuid": util.get_uuid(clazz)})
            )

        # Validation
        if employee:
            await validator.is_date_range_in_employee_range(employee, new_from, new_to)

        if employee_uuid and org_unit_uuid and it_user_uuid:
            validation = await ITAssociationUniqueGroupValidation.from_mo_objects(
                dict(
                    tilknyttedebrugere=employee_uuid,
                    tilknyttedeenheder=org_unit_uuid,
                ),
            )
            validation.update_validation_item(
                association_uuid,
                dict(
                    employee_uuid=employee_uuid,
                    org_unit_uuid=org_unit_uuid,
                    it_user_uuid=it_user_uuid,
                ),
            ).validate()

        if employee_uuid and it_user_uuid and (await is_class_uuid_primary(primary)):
            validation = await ITAssociationPrimaryGroupValidation.from_mo_objects(
                dict(tilknyttedebrugere=employee_uuid),
            )
            validation.update_validation_item(
                association_uuid,
                dict(
                    employee_uuid=employee_uuid,
                    it_user_uuid=it_user_uuid,
                    it_system_uuid=(await self._get_it_system_uuid(it_user_uuid)),
                    is_primary=True,
                ),
            ).validate()

        payload = common.update_payload(
            new_from, new_to, update_fields, original, payload
        )
        bounds_fields = list(
            mapping.ASSOCIATION_FIELDS.difference({x[0] for x in update_fields})
        )
        payload = common.ensure_bounds(
            new_from, new_to, bounds_fields, original, payload
        )

        self.payload = payload
        self.uuid = association_uuid
        self.trigger_dict.update(
            {
                "employee_uuid": employee_uuid,
                "org_unit_uuid": org_unit_uuid,
            }
        )

    async def prepare_terminate(self, request: Dict[Any, Any]):
        """Initialize a 'termination' request. Performs validation and all
        necessary processing

        Unlike the other handlers for ``organisationfunktion``, this
        one checks for and handles the ``vacate`` field in the
        request. If this is set, the manager is merely marked as
        *vacant*, i.e. without an employee or person.

        :param request: A dict containing a request

        """
        if util.checked_get(request, "vacate", False):
            self.termination_field = mapping.USER_FIELD
            self.termination_value = {}

        await super().prepare_terminate(request)

    async def _get_it_system_uuid(self, it_user_uuid: str) -> str:
        from ..handler.impl.it import ItSystemBindingReader

        connector = lora.Connector()
        reader = ItSystemBindingReader()
        it_system_uuids = {
            it_user[mapping.ITSYSTEM][mapping.UUID]
            for it_user in await reader.get(connector, {"uuid": it_user_uuid})
        }
        return one(it_system_uuids)
