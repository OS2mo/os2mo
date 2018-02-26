#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import urllib

import freezegun

from .. import util
from mora import app
from mora.converters import addr


class AddrTests(util.TestCase):
    '''Address conversion and autocomplete tests'''

    def create_app(self):
        app.app.config['DEBUG'] = False
        app.app.config['TESTING'] = True
        app.app.config['LIVESERVER_PORT'] = 0
        app.app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False

        return app.app

    @util.mock()
    def test_fetch_address_invalid_args(self, m):
        self.assertRequestFails('/mo/addressws/geographical-location', 501)
        self.assertRequestFails('/mo/addressws/geographical-location?asd', 501)
        self.assertRequestFails('/mo/addressws/geographical-location?asd=42',
                                501)
        self.assertRequestFails('/mo/addressws/geographical-location?vejnavn=',
                                501)

    @freezegun.freeze_time('2017-01-01')
    @util.mock('dawa.json')
    def test_autocomplete_address(self, mock):
        aarhus_road = urllib.parse.quote_plus('Åbogade 15')

        self.assertRequestResponse(
            '/mo/addressws/geographical-location?vejnavn=' + aarhus_road,
            util.get_fixture('addressws/aabogade.json'),
        )

        self.assertRequestResponse(
            '/mo/addressws/geographical-location?'
            'local=456362c4-0ee4-4e5e-a72c-751239745e62'
            '&vejnavn=' + aarhus_road,
            util.get_fixture('addressws/aabogade.json'),
        )

        cph_road = urllib.parse.quote_plus('Pilestræde 43')

        self.assertRequestResponse(
            '/mo/addressws/geographical-location?vejnavn=' + cph_road,
            util.get_fixture('addressws/pilestraede.json'),
        )

        self.assertRequestResponse(
            '/mo/addressws/geographical-location?'
            'local=456362c4-0ee4-4e5e-a72c-751239745e62'
            '&vejnavn=' + cph_road,
            []
        )

    @util.mock()
    def test_should_raise_exception_for_unknown_address(self, mock):
        mock.get('http://dawa.aws.dk/adresser/unknown', status_code=404)
        with self.assertRaises(KeyError):
            addr.get_address('unknown')
