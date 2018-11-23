#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import json
import os
import uuid

import requests_mock

from mora.importing import processors

from . import util


class MockTests(util.TestCase):
    maxDiff = None

    @util.mock('importing-wash.json')
    def test_addr_wash(self, m):
        w = processors.wash_address
        f = processors._fetch

        with self.subTest('mocking'):
            with self.assertRaises(requests_mock.MockException):
                f(uuid.uuid4())

            with self.assertRaises(requests_mock.MockException):
                f('kaflaflibob')

            f.cache.clear()
            f.cache['kaflaflibob', ] = None

            self.assertIsNone(f('kaflaflibob'))

            with self.assertRaises(requests_mock.MockException):
                f(uuid.uuid4())

        f.cache.clear()

        self.assertEqual(w('', None, None),
                         None)

        self.assertEqual(w('Rådhuspladsen', 8100, 'Århus C'),
                         '9b9a6a18-ffb7-4ece-a7f1-5368812e4719')

        self.assertEqual(w('Rådhuset', '8100', 'Aarhus C'),
                         '9b9a6a18-ffb7-4ece-a7f1-5368812e4719')

        self.assertEqual(w('Skejbygårdsvej 14-16', 8240, 'Risskov'),
                         None)

        self.assertEqual(w('Runevej 107-109', 8210, 'Aarhus V'),
                         '209b75e7-a662-4224-9e3d-64ef1f16eab0')

        self.assertEqual(w('Jettesvej 2, Hus 1', 8220, 'Brabrand'),
                         '2240aef2-7636-40b6-8c19-8f3e4dd65710')

        self.assertEqual(w('Grundtvigsvej 14, kld.', 8260, 'Viby J'),
                         None)
