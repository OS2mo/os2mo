#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

"""Manager
-------

This section describes how to interact with employee manager roles.

"""
import uuid

from . import address
from . import handlers
from . import org
from .validation import validator
from .. import common
from .. import lora
from .. import mapping
from .. import util
from ..triggers import Trigger

SEARCH_FIELDS = {
    'e': 'tilknyttedebrugere',
    'ou': 'tilknyttedeenheder'
}


class ManagerRequestHandler(handlers.OrgFunkRequestHandler):
    role_type = 'manager'
    function_key = mapping.MANAGER_KEY

    def prepare_create(self, req):
        """ To create a vacant manager postition, set employee_uuid to None
        and set a value org_unit_uuid """
        org_unit = util.checked_get(req, mapping.ORG_UNIT,
                                    {}, required=True)
        org_unit_uuid = util.get_uuid(org_unit, required=True)

        employee = util.checked_get(req, mapping.PERSON, {}, required=False)
        employee_uuid = util.get_uuid(employee, required=False)

        valid_from, valid_to = util.get_validities(req)

        org_uuid = org.get_configured_organisation(
            util.get_mapping_uuid(req, mapping.ORG, required=False))["uuid"]

        manager_type_uuid = util.get_mapping_uuid(req, mapping.MANAGER_TYPE)
        manager_level_uuid = util.get_mapping_uuid(req, mapping.MANAGER_LEVEL)

        responsibilities = util.checked_get(req, mapping.RESPONSIBILITY, [])

        opgaver = [
            {
                'objekttype': 'lederansvar',
                'uuid': util.get_uuid(responsibility)
            }
            for responsibility in responsibilities
        ]

        func_id = util.get_uuid(req, required=False) or str(uuid.uuid4())
        bvn = util.checked_get(req, mapping.USER_KEY, func_id)

        self.addresses = []
        addr_ids = []
        addresses = util.checked_get(req, mapping.ADDRESS, [])
        for address_obj in addresses:
            addr_id = str(uuid.uuid4())
            addr_ids.append(addr_id)

            address_obj['manager'] = {
                'uuid': func_id
            }
            address_obj['uuid'] = addr_id
            if not address_obj.get('validity'):
                address_obj['validity'] = util.checked_get(
                    req, mapping.VALIDITY, {})

            self.addresses.append(
                address.AddressRequestHandler(
                    address_obj,
                    mapping.RequestType.CREATE
                )
            )

        if manager_level_uuid:
            opgaver.append({
                'objekttype': 'lederniveau',
                'uuid': manager_level_uuid
            })

        # Validation
        validator.is_date_range_in_org_unit_range(
            org_unit,
            valid_from,
            valid_to
        )

        if employee:
            validator.is_date_range_in_employee_range(employee,
                                                      valid_from,
                                                      valid_to)

        manager = common.create_organisationsfunktion_payload(
            funktionsnavn=mapping.MANAGER_KEY,
            valid_from=valid_from,
            valid_to=valid_to,
            brugervendtnoegle=bvn,
            tilknyttedebrugere=[employee_uuid],
            tilknyttedeorganisationer=[org_uuid],
            tilknyttedeenheder=[org_unit_uuid],
            funktionstype=manager_type_uuid,
            opgaver=opgaver,
            tilknyttedefunktioner=addr_ids,
            integration_data=req.get(mapping.INTEGRATION_DATA),
        )

        self.payload = manager
        self.uuid = func_id
        self.trigger_dict.update({
            Trigger.EMPLOYEE_UUID: employee_uuid,
            Trigger.ORG_UNIT_UUID: org_unit_uuid
        })

    def submit(self):
        if hasattr(self, 'addresses'):
            for addr in self.addresses:
                addr.submit()
        return super().submit()

    def prepare_edit(self, req: dict):
        manager_uuid = req.get('uuid')
        # Get the current org-funktion which the user wants to change
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        original = c.organisationfunktion.get(uuid=manager_uuid)

        data = req.get('data')
        new_from, new_to = util.get_validities(data)

        # Get org unit uuid for validation purposes
        org_unit = mapping.ASSOCIATED_ORG_UNIT_FIELD(original)[0]

        payload = dict()
        payload['note'] = 'Rediger leder'

        original_data = req.get('original')
        if original_data:
            # We are performing an update
            old_from, old_to = util.get_validities(original_data)
            payload = common.inactivate_old_interval(
                old_from, old_to, new_from, new_to, payload,
                ('tilstande', 'organisationfunktiongyldighed')
            )

        update_fields = list()

        # Always update gyldighed
        update_fields.append((
            mapping.ORG_FUNK_GYLDIGHED_FIELD,
            {'gyldighed': "Aktiv"}
        ))

        try:
            attributes = mapping.ORG_FUNK_EGENSKABER_FIELD(original)[-1].copy()
        except (TypeError, LookupError):
            attributes = {}
        new_attributes = {}

        if mapping.USER_KEY in data:
            new_attributes['brugervendtnoegle'] = util.checked_get(
                data, mapping.USER_KEY, "")

        if new_attributes:
            update_fields.append((
                mapping.ORG_FUNK_EGENSKABER_FIELD,
                {
                    **attributes,
                    **new_attributes
                },
            ))

        if mapping.MANAGER_TYPE in data:
            update_fields.append((
                mapping.ORG_FUNK_TYPE_FIELD,
                {'uuid': util.get_mapping_uuid(data, mapping.MANAGER_TYPE)},
            ))

        if mapping.ORG_UNIT in data:
            update_fields.append((
                mapping.ASSOCIATED_ORG_UNIT_FIELD,
                {'uuid': util.get_mapping_uuid(data, mapping.ORG_UNIT)},
            ))

        if mapping.PERSON in data:
            employee = data.get(mapping.PERSON)
            employee_uuid = util.get_mapping_uuid(data, mapping.PERSON)

            if employee_uuid:
                update_payload = {
                    'uuid': employee_uuid,
                }
            else:
                update_payload = {
                    'uuid': '',
                    'urn': ''
                }

            update_fields.append((
                mapping.USER_FIELD,
                update_payload,
            ))
        else:
            employee = util.get_obj_value(
                original, mapping.USER_FIELD.path)[-1]

        for responsibility in util.checked_get(data, mapping.RESPONSIBILITY,
                                               []):
            update_fields.append((
                mapping.RESPONSIBILITY_FIELD,
                {
                    'objekttype': 'lederansvar',
                    'uuid': util.get_uuid(responsibility),
                },
            ))

        if mapping.MANAGER_LEVEL in data:
            update_fields.append((
                mapping.MANAGER_LEVEL_FIELD,
                {
                    'objekttype': 'lederniveau',
                    'uuid': util.get_mapping_uuid(data, mapping.MANAGER_LEVEL),
                },
            ))

        self.addresses = []
        for address_obj in util.checked_get(data, mapping.ADDRESS, []):

            addr_uuid = address_obj.get(mapping.UUID)

            # if UUID, perform update
            if addr_uuid:
                addr_handler = address.AddressRequestHandler(
                    {
                        'data': {
                            **address_obj,
                            'validity': data.get(mapping.VALIDITY)
                        },
                        'uuid': address_obj.get(mapping.UUID)
                    },
                    mapping.RequestType.EDIT
                )
            else:
                addr_uuid = str(uuid.uuid4())
                addr_handler = address.AddressRequestHandler(
                    {
                        'uuid': addr_uuid,
                        'manager': {
                            'uuid': manager_uuid
                        },
                        'validity': data.get(mapping.VALIDITY),
                        **address_obj,
                    },
                    mapping.RequestType.CREATE
                )

            update_fields.append((
                mapping.ASSOCIATED_MANAGER_ADDRESSES_FIELD,
                {
                    'uuid': addr_uuid
                },
            ))

            self.addresses.append(addr_handler)

        payload = common.update_payload(new_from, new_to, update_fields,
                                        original,
                                        payload)

        bounds_fields = list(
            mapping.MANAGER_FIELDS.difference({x[0] for x in update_fields}))
        payload = common.ensure_bounds(new_from, new_to, bounds_fields,
                                       original,
                                       payload)

        validator.is_date_range_in_org_unit_range(org_unit, new_from,
                                                  new_to)

        if employee:
            validator.is_date_range_in_employee_range(employee, new_from,
                                                      new_to)

        validator.is_distinct_responsibility(update_fields)

        self.payload = payload
        self.uuid = manager_uuid
        self.trigger_dict.update({
            Trigger.ORG_UNIT_UUID: util.get_uuid(org_unit, required=False),
            Trigger.EMPLOYEE_UUID: (
                util.get_mapping_uuid(data, mapping.PERSON) or
                mapping.USER_FIELD.get_uuid(original)
            )
        })

    def prepare_terminate(self, request: dict):
        """Initialize a 'termination' request. Performs validation and all
        necessary processing

        Unlike the other handlers for ``organisationfunktion``, this
        one checks for and handles the ``vacate`` field in the
        request. If this is set, the manager is merely marked as
        *vacant*, i.e. without an employee or person.

        :param request: A dict containing a request

        """
        if util.checked_get(request, 'vacate', False):
            self.termination_field = mapping.USER_FIELD
            self.termination_value = {}

        super().prepare_terminate(request)
