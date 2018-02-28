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


class Addresses(common.AbstractRelationDetail):
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

                    keys.VALIDITY: {
                        keys.FROM: util.to_iso_time(
                            common.get_effect_from(addrrel),
                        ),
                        keys.TO: util.to_iso_time(
                            common.get_effect_to(addrrel),
                        ),
                    }
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


def get_relation_for(classobj, value, start, end):
    scope = classobj['scope']

    effect = {
        'from': util.to_lora_time(start),
        'to': util.to_lora_time(end),
    }

    if scope == 'DAR':
        if not util.is_uuid(value):
            raise ValueError('{!r} is not a valid address UUID!'.format(value))

        return {
            'uuid': value,
            'objekttype': classobj['uuid'],
            'virkning': effect,
        }

    elif scope in addr.URN_FORMATS:
        return {
            'urn': addr.URN_FORMATS[scope].format(value),
            'objekttype': classobj['uuid'],
            'virkning': effect,
        }

    else:
        raise ValueError('unknown address scope {!r}!'.format(scope))


def create_address(employee_uuid, req):
    c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
    original = c.bruger.get(uuid=employee_uuid)

    # we're editing a many to many relation, so inline the logic for simplicity
    orig_addresses = original['relationer']['adresser'][:]

    new_addreses = [
        get_relation_for(
            req[keys.ADDRESS_TYPE],
            req[keys.ADDRESS],
            common.get_valid_from(req),
            common.get_valid_to(req),
        )
    ]

    payload = {
        'relationer': {
            'adresser': orig_addresses + new_addreses,
        },
        'note': 'Tilføj adresse',
    }

    c.bruger.update(payload, employee_uuid)


def edit_address(employee_uuid, req):

    c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
    original = c.bruger.get(uuid=employee_uuid)

    old_entry = req.get('original')
    new_entry = req.get('data')

    valid_from = common.get_valid_from(new_entry, old_entry)
    valid_to = common.get_valid_to(new_entry, old_entry)

    if not old_entry:
        raise ValueError('original required!')

    old_from = common.get_valid_from(old_entry)
    old_to = common.get_valid_to(old_entry)

    old_rel = get_relation_for(
        old_entry[keys.ADDRESS_TYPE],
        old_entry[keys.ADDRESS_PRETTY],
        start=old_from,
        end=old_to,
    )

    new_rel = get_relation_for(
        new_entry.get(keys.ADDRESS_TYPE) or old_entry[keys.ADDRESS_TYPE],
        new_entry.get('value') or old_entry[keys.ADDRESS_PRETTY],
        start=valid_from,
        end=valid_to,
    )

    addresses = common.replace_relation_value(
        original['relationer']['adresser'],
        old_rel, new_rel,
    )

    payload = {
        'relationer': {
            'adresser': addresses,
        }
    }

    c.bruger.update(payload, employee_uuid)


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
