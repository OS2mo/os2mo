#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import unittest
import copy

import freezegun

from mora import lora
from mora import util

from .. import util as test_util


class SimpleTests(unittest.TestCase):
    maxDiff = None

    def _apply_restrictions_for(self, value, validity=None):
        loraparams, func = lora._get_restrictions_for(validity=validity)

        with self.subTest('checking that effective date has the same effect '
                          'as running at that time'):
            with freezegun.freeze_time('2001-01-01 00:00:00', tz_offset=+1):
                old = lora._get_restrictions_for(validity=validity)
                oldtime = util.unparsedate(util.now().date())

            with freezegun.freeze_time('2011-01-01 00:00:00', tz_offset=+1):
                backdated = lora._get_restrictions_for(validity=validity,
                                                       effective_date=oldtime)
                new = lora._get_restrictions_for(validity=validity)

            self.assertEqual(old[0], backdated[0])
            self.assertEqual(old[1]([value]), backdated[1]([value]))

        return func([value])[0]

    @freezegun.freeze_time('2017-12-31 00:00:00', tz_offset=+1)
    @test_util.mock()
    def test_present_restrictions(self, m):
        obj = {
            "attributter": {
                "organisationenhedegenskaber": [
                    {
                        "brugervendtnoegle": "root",
                        "enhedsnavn": "Overordnet Enhed",
                        "virkning": {
                            "from": "2017-01-01 12:00:00+01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False,
                        },
                    },
                ],
            },
        }

        self.assertEquals(obj, self._apply_restrictions_for(obj))
        self.assertEquals(obj, self._apply_restrictions_for(obj, 'present'))

    @freezegun.freeze_time('2017-12-31 00:00:00', tz_offset=+1)
    @test_util.mock()
    def test_past_restrictions(self, m):
        obj = {
            "attributter": {
                "organisationenhedegenskaber": [
                    {
                        "brugervendtnoegle": "root",
                        "enhedsnavn": "Overordnet Enhed",
                        "virkning": {
                            "from": "2016-01-01 12:00:00+01",
                            "from_included": True,
                            "to": "2017-01-01 12:00:00+01",
                            "to_included": False,
                        },
                    },
                    {
                        "brugervendtnoegle": "root",
                        "enhedsnavn": "Overordnet Enhed",
                        "virkning": {
                            "from": "2017-01-01 12:00:00+01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False,
                        },
                    },
                ],
            },
        }

        # the second entry is current
        expected = copy.deepcopy(obj)
        expected["attributter"]["organisationenhedegenskaber"].pop(1)

        self.assertEquals(expected, self._apply_restrictions_for(obj, 'past'))

    @freezegun.freeze_time('2016-12-31 00:00:00', tz_offset=+1)
    @test_util.mock()
    def test_future_restrictions(self, m):
        obj = {
            "attributter": {
                "organisationenhedegenskaber": [
                    {
                        "brugervendtnoegle": "root",
                        "enhedsnavn": "Overordnet Enhed",
                        "virkning": {
                            "from": "2016-01-01 12:00:00+01",
                            "from_included": True,
                            "to": "2017-01-01 12:00:00+01",
                            "to_included": False,
                        },
                    },
                    {
                        "brugervendtnoegle": "root",
                        "enhedsnavn": "Overordnet Enhed",
                        "virkning": {
                            "from": "2017-01-01 12:00:00+01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False,
                        },
                    },
                ],
            },
        }

        # the first entry is current
        expected = copy.deepcopy(obj)
        expected["attributter"]["organisationenhedegenskaber"].pop(0)

        actual = self._apply_restrictions_for(obj, 'future')

        self.assertEquals(expected, actual)
