#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import freezegun

from tests import util


class TestInvalidItSystem(util.TestCase):
    @freezegun.freeze_time('2018-03-20')
    @util.mock('invalid-itsystem.json')
    def test_invalid_system(self, m):
        userid = '34705881-8af9-4254-ac3f-31738eae0be8'

        self.assertRequestResponse(
            '/service/e/{}/details/it'.format(userid),
            [
                {
                    'name': 'Lokal Rammearkitektur',
                    'reference': None,
                    'system_type': None,
                    'user_key': 'LoRA',
                    'uuid': '990255f7-44c7-4fec-9ef8-27fe73763afd',
                    'validity': {
                        'from': '2018-03-05T08:47:00+01:00', 'to': None,
                    },
                },
                {
                    'name': 'Active Directory',
                    'reference': None,
                    'system_type': None,
                    'user_key': 'AD',
                    'uuid': 'a7ecd46a-9d70-4170-bde9-9bf44cf8632b',
                    'validity': {
                        'from': '2018-03-14T08:58:00+01:00', 'to': None,
                    },
                },
                {
                    'name': 'Lokal Rammearkitektur',
                    'reference': None,
                    'system_type': None,
                    'user_key': 'LoRA',
                    'uuid': '990255f7-44c7-4fec-9ef8-27fe73763afd',
                    'validity': {
                        'from': '2018-03-19T08:57:00+01:00', 'to': None,
                    },
                },
                {
                    'name': 'Lokal Rammearkitektur',
                    'reference': None,
                    'system_type': None,
                    'user_key': 'LoRA',
                    'uuid': '990255f7-44c7-4fec-9ef8-27fe73763afd',
                    'validity': {
                        'from': '2018-03-19T09:21:00+01:00', 'to': None,
                    },
                },
            ],
        )
