#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import re

from .. import lora
from .. import util


@util.cached
def _fetch(k):
    r = lora.session.get('http://dawa.aws.dk/datavask/adresser',
                         params={
                             'betegnelse': k,
                         })
    r.raise_for_status()

    addrinfo = r.json()

    if addrinfo["kategori"] == 'A' or len(addrinfo['resultater']) == 1:
        return addrinfo['resultater'][0]['adresse']['id']


def wash_address(addrstring, postalcode, postaldistrict):
    if not addrstring:
        return None

    # first, try a direct lookup...
    v = _fetch('{}, {} {}'.format(
        addrstring.strip(), postalcode, postaldistrict.strip(),
    ))

    # ...and return it without further processing if found
    if v:
        return v

    # now, try a bit of massaging
    if str(postalcode) == '8100':
        postalcode = '8000'

    q = addrstring.strip()

    if re.search('\s*-\s*\d+\Z', q):
        q = re.sub('-\d+\Z', '', q)

    if q in ('Rådhuspladsen', 'Rådhuset') and str(postalcode) == '8000':
        q = 'Rådhuspladsen 2'

    if q.lower().startswith('dokk1'):
        q = 'Hack Kampmanns Plads 2'

    v = _fetch('{}, {} {}'.format(
        q, postalcode, postaldistrict
    ))

    if v:
        return v

    if ',' in q:
        q = q.rsplit(',', 1)[0]

    q = re.sub(r'(\s*-\s*\d+)+\Z', '', q)

    v = _fetch('{}, {} {}'.format(
        q, postalcode, postaldistrict
    ))

    if v:
        return v

    if ' - ' in q:
        for p in re.split('\s+-\s+', q):
            v = _fetch('{}, {} {}'.format(
                p, postalcode, postaldistrict
            ))

            if v:
                return v

    return None
