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
import operator
import flask

from . import address
from . import handlers
from . import orgunit
from . import facet
from . import employee
from .validation import validator
from .. import common
from .. import lora
from .. import mapping
from .. import util

SEARCH_FIELDS = {
    'e': 'tilknyttedebrugere',
    'ou': 'tilknyttedeenheder'
}


class ManagerRequestHandler(handlers.OrgFunkReadingRequestHandler):

    __slots__ = ()
    role_type = 'manager'
    function_key = mapping.MANAGER_KEY

    @classmethod
    def finder(cls, c, type, objid):

        found = super().finder(c, type, objid)
        if type == "e":
            return found

        if not found and util.get_args_flag("inherit_manager"):
            while not found:
                ou = orgunit.get_one_orgunit(
                    c, objid, details=orgunit.UnitDetails.FULL
                )
                if not ou or mapping.PARENT not in ou:
                    return found
                upperid = ou[mapping.PARENT][mapping.UUID]
                found = super().finder(c, type, upperid)
        return found

    @classmethod
    def get_one_mo_object(cls, effect, start, end, funcid):
        c = common.get_connector()

        person = mapping.USER_FIELD.get_uuid(effect)
        manager_type = mapping.ORG_FUNK_TYPE_FIELD.get_uuid(effect)
        manager_level = mapping.MANAGER_LEVEL_FIELD.get_uuid(effect)
        addresses = list(mapping.FUNCTION_ADDRESS_FIELD.get_uuids(effect))
        responsibilities = list(mapping.RESPONSIBILITY_FIELD.get_uuids(effect))
        org_unit = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)
        props = mapping.ORG_FUNK_EGENSKABER_FIELD(effect)[0]

        func = {
            mapping.UUID: funcid,
            mapping.RESPONSIBILITY: sorted([
                facet.get_one_class(c, classid, classobj)
                for classid, classobj in c.klasse.get_all(
                    uuid=responsibilities
                )
            ], key=lambda r: r[mapping.NAME]),
            mapping.ORG_UNIT: orgunit.get_one_orgunit(
                c, org_unit,
                details=orgunit.UnitDetails.MINIMAL),
            mapping.VALIDITY: {
                mapping.FROM: util.to_iso_date(start),
                mapping.TO: util.to_iso_date(
                    end, is_end=True)
            },
            mapping.ADDRESS: [],
            mapping.USER_KEY: props['brugervendtnoegle'],
        }

        for uuid in addresses:
            orgfunc = c.organisationfunktion.get(uuid=uuid)
            try:
                addr = address.get_one_address(orgfunc)
            except IndexError as e:
                # empty ["relationer"]["adresser"]
                continue
            addr["address_type"] = address.get_address_type(orgfunc)
            addr["uuid"] = uuid
            func[mapping.ADDRESS].append(addr)

        func[mapping.ADDRESS] = sorted(
            func[mapping.ADDRESS],
            key=operator.itemgetter(mapping.NAME)
        )

        if person:
            func[mapping.PERSON] = employee.get_one_employee(c, person)
        else:
            func[mapping.PERSON] = None

        if manager_type:
            func[mapping.MANAGER_TYPE] = facet.get_one_class(c, manager_type)
        else:
            func[mapping.MANAGER_TYPE] = None

        if manager_level:
            func[mapping.MANAGER_LEVEL] = facet.get_one_class(c, manager_level)
        else:
            func[mapping.MANAGER_LEVEL] = None

        return func

    def prepare_create(self, req):
        """ To create a vacant manager postition, set employee_uuid to None
        and set a value org_unit_uuid """
        c = lora.Connector()

        org_unit = util.checked_get(req, mapping.ORG_UNIT,
                                    {}, required=True)
        org_unit_uuid = util.get_uuid(org_unit, required=True)

        employee = util.checked_get(req, mapping.PERSON, {}, required=False)
        employee_uuid = util.get_uuid(employee, required=False)

        # TODO: Figure out what to do with this
        valid_from, valid_to = util.get_validities(req)

        org_uuid = (
            c.organisationenhed.get(org_unit_uuid)
            ['relationer']['tilhoerer'][0]['uuid']
        )

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
                    handlers.RequestType.CREATE
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

        validator.is_edit_from_date_before_today(new_from)

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

        if mapping.USER_KEY in data:
            update_fields.append((
                mapping.ORG_FUNK_EGENSKABER_FIELD,
                {'brugervendtnoegle': data[mapping.USER_KEY]},
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

            update_fields.append((
                mapping.USER_FIELD,
                {'uuid': employee_uuid} if employee_uuid else {},
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
                    handlers.RequestType.EDIT
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
                    handlers.RequestType.CREATE
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
