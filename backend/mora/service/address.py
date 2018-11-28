#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
'''Addresses
---------
.. _address:

Within the context of MO, we have two forms of addresses, `DAR`_ and
everything else. **DAR** is short for *Danmarks Adresseregister* or
the *Address Register of Denmark*, and constitutes a UUID representing a
DAWA address or access address. We represent other addresses merely
through their textual value.

.. tip::

  See also the `official documentation
  <http://dawa.aws.dk/dok/adresser>`_ — in Danish — on DAR addresses.

Before writing a DAR address, a UI or client should convert the
address string to a UUID using either their API or the
:http:get:`/service/o/(uuid:orgid)/address_autocomplete/` endpoint.

Each installation supports different types of addresses. To obtain
that list, query the :http:get:`/service/o/(uuid:orgid)/f/(facet)/`
endpoint::

   $ curl http://$SERVER_NAME:5000/service/o/$ORGID/f/address_type

An example result:

.. sourcecode:: json

  {
    "data": {
      "items": [
        {
          "example": "20304060",
          "name": "Telefonnummer",
          "scope": "PHONE",
          "user_key": "Telefon",
          "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec"
        },
        {
          "example": "<UUID>",
          "name": "Adresse",
          "scope": "DAR",
          "user_key": "Adresse",
          "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed"
        },
        {
          "example": "test@example.com",
          "name": "Emailadresse",
          "scope": "EMAIL",
          "user_key": "Email",
          "uuid": "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0"
        },
        {
          "example": "5712345000014",
          "name": "EAN",
          "scope": "EAN",
          "user_key": "EAN",
          "uuid": "e34d4426-9845-4c72-b31e-709be85d6fa2"
        }
      ],
      "offset": 0,
      "total": 4
    },
    "name": "address_type",
    "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/address_type/",
    "user_key": "Adressetype",
    "uuid": "e337bab4-635f-49ce-aa31-b44047a43aa1"
  }

The following scopes are available:

DAR
      UUID of a `DAR`_, as found through the API. Please
      note that this requires performing separate calls to convert
      this value to and from human-readable strings.

EMAIL
      An email address, as specified by :rfc:`5322#section-3.4`.

PHONE
      A phone number.

WWW
      An HTTP or HTTPS URL, as specified by :rfc:`1738`.

EAN
      Number for identification for accounting purposes.

PNUMBER
      A production unit number, as registered with the Danish CVR.


Reading
^^^^^^^

An example of reading the main two different types of addresses:

.. sourcecode:: json

  [
    {
      "address_type": {
        "example": "20304060",
        "name": "Telefonnummer",
        "scope": "PHONE",
        "user_key": "Telefon",
        "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec"
      },
      "href": "tel:+4587150000",
      "name": "8715 0000",
      "urn": "urn:magenta.dk:telefon:+4587150000",
      "validity": {
        "from": "2016-01-01",
        "to": null
      }
    },
    {
      "address_type": {
        "example": "<UUID>",
        "name": "Adresse",
        "scope": "DAR",
        "user_key": "Adresse",
        "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed"
      },
      "href": "https://www.openstreetmap.org/?mlon=10.199&mlat=56.171&zoom=16",
      "name": "Nordre Ringgade 1, 8000 Aarhus C",
      "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
      "validity": {
        "from": "2016-01-01",
        "to": null
      }
    }
  ]

* ``name`` is a human-readable value for displaying the address
* ``href`` should be used as a hyperlink target, if applicable
* ``urn`` and ``uuid`` are used for uniquely representing the address
  value for editing, which is detailed below.
* ``validity`` is a validity object.
* ``address_type`` is an address type object, equal to one of the types from
  the facet endpoint detailed above.

Writing
^^^^^^^

An example of objects for writing the two main types of addresses:

.. sourcecode:: json

  [
    {
      "value": "0101501234",
      "address_type": {
        "example": "5712345000014",
        "name": "EAN",
        "scope": "EAN",
        "user_key": "EAN",
        "uuid": "e34d4426-9845-4c72-b31e-709be85d6fa2"
      }
    },
    {
      "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
      "address_type": {
        "example": "<UUID>",
        "name": "Adresse",
        "scope": "DAR",
        "user_key": "Adresse",
        "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed"
      }
    }
  ]

* ``value`` the value of the address, if **not** a DAR address. This should be
  provided in human-readable format, as the backend takes care of correctly
  formatting the value into a URN
* ``uuid``: the uuid of the address, if the type **is** a DAR address.
* ``address_type`` is an address type object, equal to one of the types from
  the facet endpoint detailed above.

More information regarding creating and editing addresses can be found in the
sections on creating and editing relations for employees and organisational
units.

.. _DAR: https://dawa.aws.dk/dok/api/adresse


API
^^^

'''

import collections
import json
import re

import flask
import requests

from . import employee
from . import facet
from . import handlers
from . import orgunit
from .. import common
from .. import exceptions
from .. import lora
from .. import mapping
from .. import settings
from .. import util
from .. import validator

session = requests.Session()
session.headers = {
    'User-Agent': 'MORA/0.1',
}

URN_PREFIXES = {
    'EMAIL': 'urn:mailto:',
    'PHONE': 'urn:magenta.dk:telefon:',
    'EAN': 'urn:magenta.dk:ean:',
    'WWW': 'urn:magenta.dk:www:',
    'PNUMBER': 'urn:dk:cvr:produktionsenhed:',
    'TEXT': 'urn:text:',
}

HREF_PREFIXES = {
    'EMAIL': 'mailto:',
    'PHONE': 'tel:',
    'WWW': '',
}

DEFAULT_ERROR = 'Fejl'
NOT_FOUND = 'Ukendt'

MUNICIPALITY_CODE_PATTERN = re.compile('urn:dk:kommune:(\d+)')

blueprint = flask.Blueprint('address', __name__, static_url_path='',
                            url_prefix='/service')


def _address_string_chunks(addr):
    # loosely inspired by 'adressebetegnelse' in apiSpecification/util.js from
    # https://github.com/DanmarksAdresser/Dawa/

    yield addr['vejnavn']

    if addr.get('husnr') is not None:
        yield ' '
        yield addr['husnr']

    if addr.get('etage') is not None or addr.get('dør') is not None:
        yield ','

    if addr.get('etage') is not None:
        yield ' '
        yield addr['etage']
        yield '.'

    if addr.get('dør') is not None:
        yield ' '
        yield addr['dør']

    yield ', '

    if addr.get('supplerendebynavn') is not None:
        yield addr['supplerendebynavn']
        yield ', '

    yield addr['postnr']
    yield ' '
    yield addr['postnrnavn']


def stringify(addr):
    '''Return a string representation of the given DAWA address object'''
    return ''.join(_address_string_chunks(addr))


def fetch_from_dar(addrid):
    for addrtype in ('adresser', 'adgangsadresser',
                     'historik/adresser', 'historik/adgangsadresser'):
        r = session.get(
            'https://dawa.aws.dk/' + addrtype,
            # use a list to work around unordered dicts in Python < 3.6
            params=[
                ('id', addrid),
                ('noformat', '1'),
                ('struktur', 'mini'),
            ],
        )

        addrobjs = r.json()

        r.raise_for_status()

        if addrobjs:
            # found, escape loop!
            break

    else:
        raise LookupError('no such address {!r}'.format(addrid))

    return addrobjs.pop()


def get_one_address(rel):
    scope = rel.get('objekttype', 'DAR')

    if scope == 'DAR':
        addrid = rel['uuid']

        try:
            addrobj = fetch_from_dar(addrid)
        except Exception as exc:
            # the exception above is overly broad for a) safety and b)
            # testing -- specifically, the exception raised by
            # requests_mock does not descend from RequestException :(
            flask.current_app.logger.exception(
                'ADDRESS LOOKUP FAILED in {!r}'.format(
                    flask.request.url,
                ),
            )

            return {
                mapping.NAME: NOT_FOUND,
                mapping.HREF: None,
                mapping.UUID: addrid,
                mapping.ERROR: str(exc),
            }

        return {
            mapping.HREF: (
                # link to the location on OSM; historical addresses
                # may lack coordinates
                'https://www.openstreetmap.org/'
                '?mlon={x}&mlat={y}&zoom=16'.format(**addrobj)
                if 'x' in addrobj and 'y' in addrobj else None
            ),

            mapping.NAME: stringify(addrobj),
            mapping.UUID: addrid,
        }

    elif scope in URN_PREFIXES:
        prefix = URN_PREFIXES[scope]

        urn = rel['urn']

        if not urn.startswith(prefix):
            exceptions.ErrorCodes.E_INVALID_INPUT(
                'invalid urn {!r}'.format(rel['urn']),
            )

        name = urn[len(prefix):]
        href = (
            HREF_PREFIXES[scope] + name
            if scope in HREF_PREFIXES
            else None
        )

        if scope == 'PHONE':
            name = re.sub(r'^(\+45)(\d{8})$', r'\2', name)
        elif scope == 'TEXT':
            name = util.urnunquote(name)

        return {
            mapping.HREF: href,

            mapping.NAME: name,
            mapping.URN: urn,
        }

    else:
        exceptions.ErrorCodes.E_INVALID_INPUT(
            'invalid address scope {!r}'.format(scope),
        )


def get_id_and_type(req: dict):
    employee_uuid = util.get_mapping_uuid(req, mapping.PERSON)
    org_unit_uuid = util.get_mapping_uuid(req, mapping.ORG_UNIT)

    # this is logical xor, negated
    if (employee_uuid is not None) == (org_unit_uuid is not None):
        exceptions.ErrorCodes.E_INVALID_INPUT(
            'must specify only one of {} and {}!'.format(
                mapping.PERSON,
                mapping.ORG_UNIT,
            ),
            employee_uuid=employee_uuid,
            org_unit_uuid=org_unit_uuid,
            obj=req,
        )

    if employee_uuid is not None:
        return employee_uuid, 'e'
    else:
        assert org_unit_uuid is not None
        return org_unit_uuid, 'ou'


def get_scope_and_original(obj_uuid, obj_type):
    c = lora.Connector()

    if obj_type == 'e':
        scope = c.bruger
    else:
        assert obj_type == 'ou'
        scope = c.organisationenhed

    obj = scope.get(
        uuid=obj_uuid,
        virkningfra='-infinity',
        virkningtil='infinity',
    )

    if not obj:
        if obj_type == 'e':
            exceptions.ErrorCodes.E_USER_NOT_FOUND(uuid=obj_uuid)
        else:
            exceptions.ErrorCodes.E_ORG_UNIT_NOT_FOUND(uuid=obj_uuid)

    return scope, obj


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


class ProperAddressRequestHandler(handlers.OrgFunkRequestHandler):
    __slots__ = ()

    role_type = 'address'
    function_key = mapping.ADDRESS_KEY

    def prepare_create(self, req):
        c = lora.Connector()

        org_unit_uuid = util.get_mapping_uuid(req, mapping.ORG_UNIT,
                                              required=False)

        employee_uuid = util.get_mapping_uuid(req, mapping.PERSON,
                                              required=False)

        valid_from, valid_to = util.get_validities(req)

        # Validation
        if org_unit_uuid:
            validator.is_date_range_in_org_unit_range(org_unit_uuid,
                                                      valid_from,
                                                      valid_to)

            unitobj = c.organisationenhed.get(org_unit_uuid)
            orgid = mapping.BELONGS_TO_FIELD(unitobj)[0]['uuid']

        if employee_uuid:
            validator.is_date_range_in_employee_range(req[mapping.PERSON],
                                                      valid_from,
                                                      valid_to)

            employeeobj = c.bruger.get(employee_uuid)
            orgid = mapping.BELONGS_TO_FIELD(employeeobj)[0]['uuid']

        # TODO: validate that the date range is in
        # the validity of the IT system!

        addrobj = util.checked_get(req, mapping.ADDRESS, {})
        typeobj = util.checked_get(req, mapping.ADDRESS_TYPE, {})
        function_type = util.get_mapping_uuid(req, mapping.ADDRESS_TYPE,
                                              required=True)

        scope = util.checked_get(typeobj, 'scope', '', required=True)

        if scope == 'DAR':
            addresses = [
                {
                    'objekttype': scope,
                    'uuid': util.get_uuid(addrobj),
                },
            ]

            bvn = stringify(fetch_from_dar(util.get_uuid(addrobj)))

        elif scope in URN_PREFIXES:
            bvn = urn = util.checked_get(addrobj, mapping.VALUE, '',
                                         required=True)
            prefix = URN_PREFIXES[scope]

            if scope == 'PHONE':
                urn = re.sub(r'\s+', '', urn)

                if not urn.startswith('+'):
                    urn = '+45' + urn
            elif scope == 'TEXT':
                # make sure that we roundtrip uppercase letters properly!
                urn = util.urnquote(urn)

            if not util.is_urn(urn):
                urn = prefix + urn

            addresses = [
                {
                    'objekttype': scope,
                    'urn': urn,
                },
            ]

        func = common.create_organisationsfunktion_payload(
            funktionsnavn=mapping.ADDRESS_KEY,
            valid_from=valid_from,
            valid_to=valid_to,
            brugervendtnoegle=bvn,
            funktionstype=function_type,
            adresser=addresses,
            tilknyttedebrugere=[employee_uuid] if employee_uuid else [],
            tilknyttedeorganisationer=[orgid],
            tilknyttedeenheder=[org_unit_uuid] if org_unit_uuid else [],
        )

        self.payload = func
        self.uuid = util.get_uuid(req, required=False)

    def prepare_edit(self, req: dict):
        pass
