#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

'''
Address
-------

This section describes how to interact with addresses.

'''

import itertools
import re

import flask
import parse
import requests

from .. import lora
from .. import util
from ..converters import addr

from . import common
from . import facet
from . import keys

HREF_FORMATS = {
    'EMAIL': 'mailto:{}',
    'PHONE': 'tel:+45{}',
    'WWW': '{}',
}

MUNICIPALITY_CODE_PATTERN = re.compile('urn:dk:kommune:(\d+)')

blueprint = flask.Blueprint('address', __name__, static_url_path='',
                            url_prefix='/service')


def get_relation_for(classobj, value):
    scope = classobj['scope']

    if scope == 'DAR':
        if not util.is_uuid(value):
            raise ValueError(
                '{!r} is not a valid address UUID!'.format(value),
            )

        r = {
            'uuid': value,
            'objekttype': classobj['uuid'],
        }

    elif scope in addr.URN_FORMATS:
        r = {
            'urn': addr.URN_FORMATS[scope].format(value),
            'objekttype': classobj['uuid'],
        }

    else:
        raise ValueError('unknown address scope {!r}!'.format(scope))

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

    if addrclass['scope'] == 'DAR':
        addrobj = addr.get_address(addrrel['uuid'])

        name = addrobj['adressebetegnelse']
        value = addrrel['uuid']
        href = (
            'https://www.openstreetmap.org/'
            '?mlon={}&mlat={}&zoom=16'.format(
                *addrobj['adgangsadresse']
                ['adgangspunkt']['koordinater']
            )
        )

    elif addrclass['scope'] in addr.URN_FORMATS:
        m = parse.parse(addr.URN_FORMATS[addrclass['scope']],
                        addrrel['urn'])

        if not m:
            raise ValueError('invalid value {!r}'.format(
                addrrel['urn'],
            ))

        name = m[0]
        value = addrrel['urn']
        href = (
            HREF_FORMATS[addrclass['scope']].format(name)
            if addrclass['scope'] in HREF_FORMATS else None
        )

    else:
        raise ValueError('invalid address scope {!r}'.format(
            addrclass['scope']),
        )

    return {
        keys.HREF: href,

        keys.NAME: name,
        keys.VALUE: value,
    }


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

        def convert(start, end, effect):
            for addrrel in effect['relationer'].get('adresser', []):
                if not c.is_effect_relevant(addrrel['virkning']):
                    continue

                yield {
                    **get_one_address(c, addrrel, class_cache),
                    keys.ADDRESS_TYPE: get_address_class(c, addrrel,
                                                         class_cache),
                    keys.VALIDITY: common.get_effect_validity(addrrel),
                }

        return flask.jsonify(
            sorted(
                itertools.chain.from_iterable(
                    itertools.starmap(
                        convert,
                        self.scope.get_effects(
                            id,
                            {
                                'relationer': (
                                    'adresser',
                                ),
                                'tilstande': (
                                    'brugergyldighed',
                                ),
                            },
                            {
                                'attributter': (
                                    'brugeregenskaber',
                                ),
                            },
                        ),
                    ),
                ),
                key=(
                    lambda v: (
                        common.get_valid_from(v) or util.negative_infinity,
                        common.get_valid_to(v) or util.positive_infinity,
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
        rel = get_relation_for(
            req[keys.ADDRESS_TYPE],
            req[keys.ADDRESS],
        )
        rel['virkning'] = common.get_validity_effect(req)

        payload = {
            'relationer': {
                'adresser': original['relationer']['adresser'] + [rel],
            },
            'note': 'Tilføj adresse',
        }

        self.scope.update(payload, id)

    def edit(self, id, req):
        original = self.scope.get(uuid=id)

        old_entry = req.get('original')
        new_entry = req.get('data')

        if not old_entry:
            raise ValueError('original required!')

        old_rel = get_relation_for(
            old_entry[keys.ADDRESS_TYPE],
            old_entry[keys.NAME],
        )
        old_rel['virkning'] = common.get_validity_effect(old_entry)

        new_rel = get_relation_for(
            new_entry.get(keys.ADDRESS_TYPE) or old_entry[keys.ADDRESS_TYPE],
            new_entry.get(keys.VALUE) or old_entry[keys.NAME],
        )
        new_rel['virkning'] = common.get_validity_effect(new_entry, old_entry)

        addresses = common.replace_relation_value(
            original['relationer']['adresser'],
            old_rel, new_rel,
        )

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
    :queryparam uuid global: Whether or not the lookup should be in the entire
        country, or contained to the municipality of the organisation

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
    global_lookup = flask.request.args.get('global', False, type=bool)

    if not global_lookup:
        org = lora.Connector().organisation.get(orgid)

        if not org:
            raise KeyError('No local municipality found!')

        for myndighed in org.get('relationer', {}).get('myndighed', []):
            m = MUNICIPALITY_CODE_PATTERN.fullmatch(myndighed.get('urn'))

            if m:
                code = int(m.group(1))
                break
        else:
            raise KeyError('No local municipality found!')
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
