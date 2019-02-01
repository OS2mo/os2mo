#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import collections
import re

import flask
import requests

from . import handlers
from .. import common
from .. import exceptions
from .. import lora
from .. import mapping
from .. import settings
from .. import util
from .. import validator
from . import facet
from . import employee
from . import orgunit

from .address_handler import base

session = requests.Session()
session.headers = {
    'User-Agent': 'MORA/0.1',
}

MUNICIPALITY_CODE_PATTERN = re.compile('urn:dk:kommune:(\d+)')

SEARCH_FIELDS = {
    'e': 'tilknyttedebrugere',
    'ou': 'tilknyttedeenheder'
}

blueprint = flask.Blueprint('address', __name__, static_url_path='',
                            url_prefix='/service')


def get_address_type(effect):
    c = lora.Connector()
    address_type_uuid = mapping.ADDRESS_TYPE_FIELD(effect)[0].get('uuid')
    return facet.get_one_class(c, address_type_uuid)


def get_one_address(effect):
    scope = mapping.SINGLE_ADDRESS_FIELD(effect)[0].get('objekttype')
    handler = base.get_handler_for_scope(scope).from_effect(effect)

    return handler.get_mo_address_and_properties()


@blueprint.route('/o/<uuid:orgid>/address_autocomplete/')
@util.restrictargs('global', required=['q'])
def address_autocomplete(orgid):
    """Perform address autocomplete, resolving both ``adgangsadresse`` and
    ``adresse``.

    :param orgid: The UUID of the organisation

    .. :quickref: Address; Autocomplete

    :queryparam str q: A query string to be used for lookup
    :queryparam boolean global: Whether or not the lookup should be in
        the entire country, or contained to the municipality of the
        organisation

    **Example Response**:

    :<jsonarr uuid uuid: A UUID of a DAR address
    :<jsonarr str name: A human readable name for the address

    .. sourcecode:: json

      [
        {
          "location": {
            "uuid": "f0396d0f-ef2d-41e5-a420-b4507b26b6fa",
            "name": "Rybergsvej 1, Sønderby, 5631 Ebberup"
          }
        },
        {
          "location": {
            "uuid": "0a3f50cb-05eb-32b8-e044-0003ba298018",
            "name": "Wild Westvej 1, 9310 Vodskov"
          }
        }
      ]

    """
    q = flask.request.args['q']
    global_lookup = util.get_args_flag('global')

    if not global_lookup:
        org = lora.Connector().organisation.get(orgid)

        if not org:
            exceptions.ErrorCodes.E_NO_LOCAL_MUNICIPALITY()

        for myndighed in org.get('relationer', {}).get('myndighed', []):
            m = MUNICIPALITY_CODE_PATTERN.fullmatch(myndighed.get('urn'))

            if m:
                code = int(m.group(1))
                break
        else:
            exceptions.ErrorCodes.E_NO_LOCAL_MUNICIPALITY()
    else:
        code = None

    #
    # In order to allow reading both access & regular addresses, we
    # autocomplete both into an ordered dictionary, with the textual
    # representation as keys. Regular addresses tend to be less
    # relevant than access addresses, so we list them last.
    #
    # The limits are somewhat arbitrary: Since access addresses mostly
    # differ by street number or similar, we only show five -- by
    # comparison, ten addresses seems apt since they may refer to
    # apartments etc.
    #

    addrs = collections.OrderedDict(
        (addr['tekst'], addr['adgangsadresse']['id'])
        for addr in session.get(
            'https://dawa.aws.dk/adgangsadresser/autocomplete',
            # use a list to work around unordered dicts in Python < 3.6
            params=[
                ('per_side', settings.AUTOCOMPLETE_ACCESS_ADDRESS_COUNT),
                ('noformat', '1'),
                ('kommunekode', code),
                ('q', q),
            ],
        ).json()
    )

    for addr in session.get(
        'https://dawa.aws.dk/adresser/autocomplete',
        # use a list to work around unordered dicts in Python < 3.6
        params=[
            ('per_side', settings.AUTOCOMPLETE_ADDRESS_COUNT),
            ('noformat', '1'),
            ('kommunekode', code),
            ('q', q),
        ],
    ).json():
        addrs.setdefault(addr['tekst'], addr['adresse']['id'])

    return flask.jsonify([
        {
            "location": {
                "name": k,
                "uuid": addrs[k],
            },
        }
        for k in addrs
    ])


class AddressRequestHandler(handlers.OrgFunkRequestHandler,
                            handlers.ReadingRequestHandler):

    __slots__ = ()

    role_type = 'address'
    function_key = mapping.ADDRESS_KEY

    @classmethod
    def get(cls, c, type, objid):

        search = {
            SEARCH_FIELDS[type]: objid
        }

        function_effects = [
            cls.get_one_mo_object(effect, start, end, funcid)
            for funcid, funcobj in c.organisationfunktion.get_all(
                funktionsnavn=cls.function_key,
                **search,
            )
            for start, end, effect in c.organisationfunktion.get_effects(
                funcobj,
                {
                    'relationer': (
                        'opgaver',
                        'adresser',
                        'organisatoriskfunktionstype',
                        'tilknyttedeenheder',
                        'tilknyttedebrugere',
                    ),
                    'tilstande': (
                        'organisationfunktiongyldighed',
                    ),
                },
                {
                    'attributter': (
                        'organisationfunktionegenskaber',
                    ),
                    'relationer': (
                        'tilhoerer',
                        'tilknyttedeorganisationer',
                        'tilknyttedeitsystemer',
                    ),
                },
            )
            if util.is_reg_valid(effect)
        ]

        return flask.jsonify(function_effects)

    @classmethod
    def get_one_mo_object(cls, effect, start, end, funcid):
        c = common.get_connector()

        address_type_uuid = mapping.ADDRESS_TYPE_FIELD(effect)[0].get('uuid')

        try:
            address_type = facet.get_one_class(c, address_type_uuid)
        except exceptions.HTTPException:
            address_type = None

        scope = mapping.SINGLE_ADDRESS_FIELD(effect)[0].get('objekttype')
        handler = base.get_handler_for_scope(scope).from_effect(effect)

        person = list(mapping.USER_FIELD.get_uuids(effect))
        org_unit = list(mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuids(effect))

        func = {
            mapping.ADDRESS_TYPE: address_type,
            mapping.VALIDITY: {
                mapping.FROM: util.to_iso_date(start),
                mapping.TO: util.to_iso_date(
                    end, is_end=True)
            },
            mapping.UUID: funcid,
            **handler.get_mo_address_and_properties()
        }
        if person:
            func[mapping.PERSON] = employee.get_one_employee(
                c, person[0])
        if org_unit:
            func[mapping.ORG_UNIT] = orgunit.get_one_orgunit(
                c, org_unit[0],
                details=orgunit.UnitDetails.MINIMAL)

        return func

    @classmethod
    def has(cls, scope, objid):
        pass

    def prepare_create(self, req):
        org_unit_uuid = util.get_mapping_uuid(req, mapping.ORG_UNIT,
                                              required=False)

        employee_uuid = util.get_mapping_uuid(req, mapping.PERSON,
                                              required=False)

        manager_uuid = util.get_mapping_uuid(req, mapping.MANAGER,
                                             required=False)

        number_of_uuids = len(
            list(filter(None, [org_unit_uuid, employee_uuid, manager_uuid])))

        if number_of_uuids is not 1:
            raise exceptions.ErrorCodes.E_INVALID_INPUT(
                'Must supply exactly one org unit UUID, '
                'employee UUID or manager UUID', obj=req)

        valid_from, valid_to = util.get_validities(req)

        orgid = util.get_mapping_uuid(req, mapping.ORG, required=True)

        typeobj = util.checked_get(req, mapping.ADDRESS_TYPE, {})
        function_type = util.get_mapping_uuid(req, mapping.ADDRESS_TYPE,
                                              required=True)

        scope = util.checked_get(typeobj, 'scope', '', required=True)

        handler = base.get_handler_for_scope(scope).from_request(req)

        # Validation
        if org_unit_uuid:
            validator.is_date_range_in_org_unit_range(req[mapping.ORG_UNIT],
                                                      valid_from,
                                                      valid_to)

        if employee_uuid:
            validator.is_date_range_in_employee_range(req[mapping.PERSON],
                                                      valid_from,
                                                      valid_to)

        func = common.create_organisationsfunktion_payload(
            funktionsnavn=mapping.ADDRESS_KEY,
            valid_from=valid_from,
            valid_to=valid_to,
            brugervendtnoegle=handler.name,
            funktionstype=function_type,
            adresser=[handler.get_lora_address()],
            tilknyttedebrugere=[employee_uuid] if employee_uuid else [],
            tilknyttedeorganisationer=[orgid],
            tilknyttedeenheder=[org_unit_uuid] if org_unit_uuid else [],
            tilknyttedefunktioner=[manager_uuid] if manager_uuid else [],
            opgaver=handler.get_lora_properties()
        )

        self.payload = func
        self.uuid = util.get_uuid(req, required=False)

    def prepare_edit(self, req: dict):
        function_uuid = util.get_uuid(req)

        # Get the current org-funktion which the user wants to change
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        original = c.organisationfunktion.get(uuid=function_uuid)

        if not original:
            exceptions.ErrorCodes.E_NOT_FOUND()

        data = req.get('data')
        new_from, new_to = util.get_validities(data)

        validator.is_edit_from_date_before_today(new_from)

        payload = {
            'note': 'Rediger Adresse',
        }

        number_of_uuids = len(
            list(filter(None, [
                data.get(mapping.PERSON),
                data.get(mapping.ORG_UNIT),
                data.get(mapping.MANAGER),
            ])))

        if number_of_uuids > 1:
            raise exceptions.ErrorCodes.E_INVALID_INPUT(
                'Must supply at most one org unit UUID, '
                'employee UUID or manager UUID', obj=req)

        original_data = req.get('original')
        if original_data:
            # We are performing an update
            old_from, old_to = util.get_validities(original_data)
            payload = common.inactivate_old_interval(
                old_from, old_to, new_from, new_to, payload,
                ('tilstande', 'organisationfunktiongyldighed')
            )

        update_fields = [
            # Always update gyldighed
            (
                mapping.ORG_FUNK_GYLDIGHED_FIELD,
                {'gyldighed': "Aktiv"}
            ),
        ]

        if mapping.PERSON in data:
            update_fields.append((
                mapping.USER_FIELD,
                {
                    'uuid':
                        util.get_mapping_uuid(data, mapping.PERSON),
                },
            ))

        if mapping.ORG_UNIT in data:
            update_fields.append((
                mapping.ASSOCIATED_ORG_UNIT_FIELD,
                {
                    'uuid':
                        util.get_mapping_uuid(data, mapping.ORG_UNIT),
                },
            ))

        if mapping.MANAGER in data:
            update_fields.append((
                mapping.ASSOCIATED_FUNCTION_FIELD,
                {
                    'uuid':
                        util.get_mapping_uuid(data, mapping.MANAGER),
                },
            ))

        if mapping.USER_KEY in data:
            update_fields.append((
                mapping.ORG_FUNK_EGENSKABER_FIELD,
                {
                    'brugervendtnoegle':
                        util.checked_get(data, mapping.USER_KEY, ''),
                },
            ))

        if mapping.VALUE in data:

            address_type = util.checked_get(
                data, mapping.ADDRESS_TYPE, {}, required=True)
            scope = util.checked_get(address_type, 'scope', '', required=True)
            type_uuid = util.get_uuid(address_type)

            handler = base.get_handler_for_scope(scope).from_request(data)

            update_fields.append((
                mapping.SINGLE_ADDRESS_FIELD,
                handler.get_lora_address(),
            ))

            update_fields.append((
                mapping.ADDRESS_TYPE_FIELD,
                {
                    'uuid': type_uuid
                }
            ))

            for prop in handler.get_lora_properties():
                update_fields.append((
                    mapping.VISIBILITY_FIELD,
                    prop
                ))

        payload = common.update_payload(new_from, new_to, update_fields,
                                        original,
                                        payload)

        bounds_fields = list(mapping.ADDRESS_FIELDS.difference(
            {x[0] for x in update_fields},
        ))
        payload = common.ensure_bounds(new_from, new_to, bounds_fields,
                                       original,
                                       payload)

        self.payload = payload
        self.uuid = function_uuid
