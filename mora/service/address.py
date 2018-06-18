#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

'''Addresses
---------

Within the context of MO, we have to forms of address, `DAR`_ and
everything else. **DAR** is short for *Danmarks Adresseregister* or
the *Address Register of Denmark*, and constitutes a UUID reprenting a
DAWA address or access address. We represent other addresses merely
through their textual value.

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

Example data
~~~~~~~~~~~~

An example of reading the main two different types of addresses:

.. sourcecode: json

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
        "from": "2016-01-01T00:00:00+01:00",
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
        "from": "2016-01-01T00:00:00+01:00",
        "to": null
      }
    }
  ]

Of these, ``name`` should be used for displaying the address and
``href`` for a hyperlink target. The ``uuid`` and ``urn`` keys
uniquely represent the address value for editing, although any such
operation should specify the entire object.

.. _DAR: http://dawa.aws.dk/dok/api/adresse


API
~~~

'''

import json
import re

import flask
import requests

from .. import exceptions
from .. import lora
from .. import util

from . import common
from . import facet
from . import keys

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
}

HREF_PREFIXES = {
    'EMAIL': 'mailto:',
    'PHONE': 'tel:',
    'WWW': '',
}

MUNICIPALITY_CODE_PATTERN = re.compile('urn:dk:kommune:(\d+)')

blueprint = flask.Blueprint('address', __name__, static_url_path='',
                            url_prefix='/service')


def get_relation_for(addrobj, fallback=None):
    typeobj = common.checked_get(addrobj, keys.ADDRESS_TYPE, {},
                                 fallback=fallback, required=True)
    scope = common.checked_get(typeobj, 'scope', '', required=True)
    validity = common.get_validity_effect(addrobj, fallback=fallback)

    r = {}

    if validity is not None:
        r['virkning'] = validity

    if scope == 'DAR':
        r['uuid'] = common.get_uuid(addrobj, fallback)
        r['objekttype'] = common.checked_get(typeobj, keys.UUID, 'DAR')

    elif scope in URN_PREFIXES:
        # this is the fallback: we want to use the 'urn' key if set
        # directly (e.g. if this is the original) or if it's present
        # in the fallback -- but with an important caveat: we always
        # want to report that the *value* is missing in the
        # exception/error message.
        if (
            keys.VALUE not in addrobj and (
                'urn' in addrobj or fallback and 'urn' in fallback
            )
        ):
            value = common.get_urn(addrobj, fallback)

        else:
            value = common.checked_get(addrobj, keys.VALUE, '', required=True)
            prefix = URN_PREFIXES[scope]

            if scope == 'PHONE':
                value = re.sub(r'\s+', '', value)

                if not value.startswith('+'):
                    value = '+45' + value

            if not util.is_urn(value):
                value = prefix + value

        r['urn'] = value
        r['objekttype'] = common.get_uuid(typeobj)

    else:
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.E_INVALID_INPUT,
            'unknown address scope {!r}!'.format(scope)
        )

    return r


def get_address_class(c, addrrel, class_cache):
    addrtype = addrrel.get('objekttype', 'DAR')

    if not util.is_uuid(addrtype):
        return {'scope': addrtype}
    else:
        return (
            class_cache[addrtype]
            if class_cache
            else facet.get_one_class(c, addrtype)
        )


def get_one_address(c, addrrel, class_cache=None):
    addrclass = get_address_class(c, addrrel, class_cache)
    addrformat = common.checked_get(addrclass, 'scope', 'DAR')

    if addrformat == 'DAR':
        # unfortunately, we cannot live with struktur=mini, as it omits
        # the formatted address :(
        r = session.get(
            'http://dawa.aws.dk/adresser/' + addrrel['uuid'],
            params={
                'noformat': '1',
            },
        )

        r.raise_for_status()

        addrobj = r.json()

        return {
            keys.ADDRESS_TYPE: addrclass,
            keys.HREF: (
                'https://www.openstreetmap.org/'
                '?mlon={}&mlat={}&zoom=16'.format(
                    *addrobj['adgangsadresse']
                    ['adgangspunkt']['koordinater']
                )
            ),

            keys.NAME: addrobj['adressebetegnelse'],
            keys.UUID: addrrel['uuid'],
        }

    elif addrformat in URN_PREFIXES:
        prefix = URN_PREFIXES[addrformat]

        urn = addrrel['urn']

        if not urn.startswith(prefix):
            raise exceptions.HTTPException(
                exceptions.ErrorCodes.E_INVALID_INPUT,
                'invalid urn {!r}'.format(addrrel['urn'])
            )

        name = urn[len(prefix):]
        href = (
            HREF_PREFIXES[addrformat] + name
            if addrformat in HREF_PREFIXES
            else None
        )

        if addrformat == 'PHONE':
            name = re.sub(r'^(\+45)(\d{8})$', r'\2', name)

        return {
            keys.ADDRESS_TYPE: addrclass,

            keys.HREF: href,

            keys.NAME: name,
            keys.URN: urn,
        }

    else:
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.E_INVALID_INPUT,
            'invalid address scope {!r}'.format(addrformat),
        )


class Addresses(common.AbstractRelationDetail):
    @staticmethod
    def has(reg):
        return(
            reg and
            reg.get('relationer') and
            reg['relationer'].get('adresser') and
            any(
                rel.get('objekttype') == 'DAR' or
                util.is_uuid(rel.get('objekttype'))
                for rel in reg['relationer']['adresser']
            )
        )

    def get(self, id):
        c = self.scope.connector

        class_cache = common.cache(facet.get_one_class, c)

        def convert(effect):
            if not effect.get('relationer'):
                return
            for addrrel in effect['relationer'].get('adresser', []):
                if not c.is_effect_relevant(addrrel['virkning']):
                    continue

                try:
                    addr = get_one_address(c, addrrel, class_cache)
                except Exception as e:
                    util.log_exception(
                        'invalid address relation {}'.format(
                            json.dumps(addrrel),
                        ),
                    )

                    continue

                addr[keys.VALIDITY] = common.get_effect_validity(addrrel)

                yield addr

        return flask.jsonify(
            sorted(
                convert(self.scope.get(id)),
                key=(
                    lambda v: (
                        common.get_valid_from(v) or util.NEGATIVE_INFINITY,
                        common.get_valid_to(v) or util.POSITIVE_INFINITY,
                        str(v[keys.NAME]),
                    )
                ),
            ),
        )

    def create(self, id, req):
        original = self.scope.get(
            uuid=id,
            virkningfra='-infinity',
            virkningtil='infinity',
        )

        # we're editing a many-to-many relation, so inline the
        # create_organisationsenhed_payload logic for simplicity
        rel = get_relation_for(req)

        addrs = original['relationer'].get('adresser', [])

        payload = {
            'relationer': {
                'adresser': addrs + [rel],
            },
            'note': 'Tilføj adresse',
        }

        self.scope.update(payload, id)

    @staticmethod
    def get_relation_for(req):
        return 'adresser', get_relation_for(req)

    def edit(self, id, req):
        original = self.scope.get(
            uuid=id,
            virkningfra='-infinity',
            virkningtil='infinity',
        )

        old_entry = common.checked_get(req, 'original', {}, required=True)
        new_entry = common.checked_get(req, 'data', {}, required=True)

        if not old_entry:
            raise exceptions.HTTPException(
                exceptions.ErrorCodes.V_ORIGINAL_REQUIRED
            )

        old_rel = get_relation_for(old_entry)
        new_rel = get_relation_for(new_entry, old_entry)

        try:
            addresses = original['relationer']['adresser']
        except KeyError:
            raise exceptions.HTTPException(
                exceptions.ErrorCodes.E_INVALID_INPUT,
                'no addresses to edit!',
                original=original
            )

        addresses = common.replace_relation_value(addresses, old_rel, new_rel)

        payload = {
            'relationer': {
                'adresser': addresses,
            }
        }

        self.scope.update(payload, id)


@blueprint.route('/o/<uuid:orgid>/address_autocomplete/')
@util.restrictargs('global', required=['q'])
def address_autocomplete(orgid):
    """Perform address autocomplete
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
    global_lookup = common.get_args_flag('global')

    if not global_lookup:
        org = lora.Connector().organisation.get(orgid)

        if not org:
            raise exceptions.HTTPException(
                exceptions.ErrorCodes.E_NO_LOCAL_MUNICIPALITY)

        for myndighed in org.get('relationer', {}).get('myndighed', []):
            m = MUNICIPALITY_CODE_PATTERN.fullmatch(myndighed.get('urn'))

            if m:
                code = int(m.group(1))
                break
        else:
            raise exceptions.HTTPException(
                exceptions.ErrorCodes.E_NO_LOCAL_MUNICIPALITY)
    else:
        code = None

    addrs = requests.get(
        'http://dawa.aws.dk/adresser/autocomplete',
        params={
            'noformat': '1',
            'kommunekode': code,
            'q': q,
        },
    ).json()

    return flask.jsonify([
        {
            "location": {
                "uuid": addr['adresse']['id'],
                "name": addr['tekst']
            }
        }
        for addr in addrs
    ])
