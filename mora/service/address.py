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
import locale

import flask
import parse

from .. import lora
from .. import util
from ..converters import addr

from . import common
from . import facet
from . import keys
from . import mapping

HREF_FORMATS = {
    'EMAIL': 'mailto:{}',
    'PHONE': 'tel:+45{}',
    'WWW': '{}',
}


class Adresses(common.AbstractRelationDetail):
    @staticmethod
    def has(objtype, reg):
        return(
            reg and
            reg.get('relationer') and reg['relationer'].get('adresser') and
            any(
                rel.get('objekttype') == 'DAR' or
                util.is_uuid(rel.get('objekttype'))
                for rel in reg['relationer']['adresser']
            )
        )

    @staticmethod
    def get(objtype, id):
        c = common.get_connector()

        if objtype == "e":
            scope = c.bruger
        else:
            assert objtype == 'ou', 'bad type ' + objtype
            scope = c.organisationenhed

        class_cache = common.cache(facet.get_one_class, c)

        def convert(start, end, effect):
            for addrrel in effect['relationer'].get('adresser', []):
                if not c.is_effect_relevant(addrrel['virkning']):
                    continue

                addrtype = addrrel.get('objekttype', 'DAR')

                addrclass = (
                    class_cache[addrtype]
                    if util.is_uuid(addrtype)
                    else dict(scope=addrtype)
                )

                if addrclass['scope'] == 'DAR':
                    addrobj = addr.get_address(addrrel['uuid'])

                    pretty_value = addrobj['adressebetegnelse']
                    raw_value = addrrel['uuid']
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
                        raise ValueError('invalid {} value {!r}'.format(
                            scope,
                            addrrel['urn'],
                        ))

                    pretty_value = m[0]
                    raw_value = addrrel['urn']
                    href = (
                        HREF_FORMATS[addrclass['scope']].format(pretty_value)
                        if addrclass['scope'] in HREF_FORMATS else None
                    )

                else:
                    raise ValueError('invalid address scope {!r}'.format(
                        addrclass['scope']),
                    )

                yield {
                    keys.ADDRESS_HREF: href,

                    keys.ADDRESS_PRETTY: pretty_value,
                    keys.ADDRESS_RAW: raw_value,
                    keys.ADDRESS_TYPE: addrclass,

                    keys.FROM: util.to_iso_time(
                        addrrel['virkning']['from'],
                    ),
                    keys.TO: util.to_iso_time(
                        addrrel['virkning']['to'],
                    ),
                }

        return flask.jsonify(
            sorted(
                itertools.chain.from_iterable(
                    itertools.starmap(
                        convert,
                        scope.get_effects(
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
                        str(v[keys.ADDRESS_PRETTY]),
                    )
                ),
            ),
        )


def create_address(employee_uuid, req):
    scope = req[keys.ADDRESS_TYPE]['scope']
    val = req[keys.ADDRESS]

    valid_from = common.get_valid_from(req)
    valid_to = common.get_valid_to(req)

    c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
    original = c.bruger.get(uuid=employee_uuid)

    if scope == 'DAR':
        if not util.is_uuid(val):
            raise ValueError('{!r} is not a valid address UUID!'.format(val))

        rel = {
            'uuid': val,
            'objekttype': req[keys.ADDRESS_TYPE]['uuid']
        }

    elif scope in addr.URN_FORMATS:
        rel = {
            'urn': addr.URN_FORMATS[scope].format(val),
            'objekttype': req[keys.ADDRESS_TYPE]['uuid'],
        }

    else:
        raise ValueError('unknown address scope {!r}!'.format(scope))

    payload = common.update_payload(
        valid_from,
        valid_to,
        [(mapping.ADDRESSES_FIELD, rel)],
        original,
        {
            'note': 'Tilføj adresse',
        },
    )

    c.bruger.update(payload, employee_uuid)
