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
import requests

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
}

HREF_PREFIXES = {
    'EMAIL': 'mailto:',
    'PHONE': 'tel:',
    'WWW': '',
}

MUNICIPALITY_CODE_PATTERN = re.compile('urn:dk:kommune:(\d+)')

blueprint = flask.Blueprint('address', __name__, static_url_path='',
                            url_prefix='/service')


def get_relation_for(classobj, addrobj, fallback=None):
    scope = common.checked_get(classobj, 'scope', '', required=True)

    if scope == 'DAR':
        return {
            'uuid': common.get_uuid(addrobj, fallback),
            'objekttype': classobj['uuid'],
        }

    elif scope in URN_PREFIXES:
        # this is the fallback: we want to use the 'urn' key if set
        # directly (e.g. if this is the original) or if it's present
        # in the fallback -- but with an important caveat: we always
        # want to report that the *value* is missing in the
        # exception/error message.
        if (
            'urn' in addrobj or
            keys.VALUE not in addrobj and fallback and 'urn' in fallback
        ):
            return {
                'urn': common.get_urn(addrobj, fallback),
                'objekttype': classobj['uuid'],
            }

        value = common.checked_get(addrobj, keys.VALUE, '', required=True)
        prefix = URN_PREFIXES[scope]

        if scope == 'PHONE':
            value = re.sub(r'\s+', '', value)

            if not value.startswith('+'):
                value = '+45' + value

        if not util.is_urn(value):
            value = prefix + value

        return {
            'urn': value,
            'objekttype': classobj['uuid'],
        }

    else:
        raise ValueError('unknown address scope {!r}!'.format(scope))


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
            raise ValueError('invalid urn {!r}'.format(
                addrrel['urn'],
            ))

        name = urn[len(prefix):]
        href = (
            HREF_PREFIXES[addrformat] + name
            if addrformat in HREF_PREFIXES
            else None
        )

        if addrformat == 'PHONE':
            name = re.sub(r'^(\+45)(\d{4})(\d{4})$', r'\2 \3', name)

        return {
            keys.HREF: href,

            keys.NAME: name,
            keys.URN: urn,
        }

    else:
        raise ValueError('invalid address scope {!r}'.format(addrformat))


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
            common.checked_get(req, keys.ADDRESS_TYPE, {}, required=True),
            req,
        )
        rel['virkning'] = common.get_validity_effect(req)

        addrs = original['relationer'].get('adresser', [])

        payload = {
            'relationer': {
                'adresser': addrs + [rel],
            },
            'note': 'Tilføj adresse',
        }

        self.scope.update(payload, id)

    def edit(self, id, req):
        original = self.scope.get(
            uuid=id,
            virkningfra='-infinity',
            virkningtil='infinity',
        )

        old_entry = common.checked_get(req, 'original', {}, required=True)
        new_entry = common.checked_get(req, 'data', {}, required=True)

        if not old_entry:
            raise ValueError('original required!')

        old_rel = get_relation_for(
            common.checked_get(old_entry, keys.ADDRESS_TYPE, {},
                               required=True),
            old_entry,
        )
        old_rel['virkning'] = common.get_validity_effect(old_entry)

        new_rel = get_relation_for(
            common.checked_get(new_entry, keys.ADDRESS_TYPE, {},
                               fallback=old_entry, required=True),
            new_entry,
            old_entry,
        )
        new_rel['virkning'] = common.get_validity_effect(new_entry, old_entry)

        try:
            addresses = original['relationer']['adresser']
        except KeyError:
            raise ValueError('no addresses to edit!')

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
