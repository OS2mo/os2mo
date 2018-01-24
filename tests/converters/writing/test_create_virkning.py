#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import freezegun
import unittest

from mora.converters import writing


class TestCreateVirkning(unittest.TestCase):
    def setUp(self):
        self.from1 = '31-12-2017'
        self.to1 = '31-12-2018'
        self.from2 = '30-12-2017'
        self.to2 = '31-12-2018'

    @freezegun.freeze_time(tz_offset=+1)
    def test_should_set_from_to_2017_12_31(self):
        self.assertEqual('2017-12-31T00:00:00+01:00',
                         writing._create_virkning(self.from1,
                                                  self.to1)['from'],
                         'From should be 2017-12-31T00:00:00+01:00')

    @freezegun.freeze_time(tz_offset=+1)
    def test_should_set_from_to_2017_12_30(self):
        self.assertEqual('2017-12-30T00:00:00+01:00',
                         writing._create_virkning(self.from2,
                                                  self.to2)['from'],
                         'From should be 2017-12-30T00:00:00+01:00')

    @freezegun.freeze_time(tz_offset=+1)
    def test_should_set_to_to_2018_12_31(self):
        self.assertEqual('2018-12-31T00:00:00+01:00',
                         writing._create_virkning(self.from2,
                                                  self.to2)['to'],
                         'To should be 2018-12-31T00:00:00+01:00')

    @freezegun.freeze_time(tz_offset=+1)
    def test_should_set_to_to_2019_12_31(self):
        req = {
            'valid-from': '30-12-2017',
            'valid-to': '31-12-2019'
        }
        self.assertEqual('2019-12-31T00:00:00+01:00',
                         writing._create_virkning(req['valid-from'],
                                                  req['valid-to'])['to'],
                         'To should be 2019-12-31T00:00:00+01:00')

    @freezegun.freeze_time(tz_offset=+1)
    def test_should_set_from_to_minus_infinity(self):
        req = {
            'valid-from': '-infinity',
            'valid-to': '31-12-2019',

        }
        self.assertEqual('-infinity',
                         writing._create_virkning(req['valid-from'],
                                                  req['valid-to'])['from'],
                         'From should be -infinity')

    @freezegun.freeze_time(tz_offset=+1)
    def test_should_set_to_to_infinity(self):
        req = {
            'valid-from': '31-12-2019',
            'valid-to': 'infinity',

        }
        self.assertEqual('infinity',
                         writing._create_virkning(req['valid-from'],
                                                  req['valid-to'])['to'],
                         'To should be infinity')

    @freezegun.freeze_time(tz_offset=+1)
    def test_should_set_from_included_to_true(self):
        self.assertEqual(True,
                         writing._create_virkning(
                             self.from1,
                             self.to1,
                             from_included=True)['from_included'],
                         'from_included should be true')

    @freezegun.freeze_time(tz_offset=+1)
    def test_should_set_from_included_to_true_by_default(self):
        self.assertEqual(True,
                         writing._create_virkning(self.from1, self.to1)[
                             'from_included'],
                         'from_included should be true')

    @freezegun.freeze_time(tz_offset=+1)
    def test_should_set_from_included_to_false(self):
        self.assertEqual(False,
                         writing._create_virkning(self.from1, self.to1,
                                                  from_included=False)[
                             'from_included'],
                         'from_included should be false')

    @freezegun.freeze_time(tz_offset=+1)
    def test_should_set_to_included_to_false(self):
        self.assertEqual(False,
                         writing._create_virkning(self.from1, self.to1,
                                                  to_included=False)[
                             'to_included'],
                         'to_included should be false')

    @freezegun.freeze_time(tz_offset=+1)
    def test_should_set_to_included_to_false_by_default(self):
        self.assertEqual(False,
                         writing._create_virkning(self.from1, self.to1)[
                             'to_included'],
                         'to_included should be false')

    @freezegun.freeze_time(tz_offset=+1)
    def test_should_set_to_included_to_true(self):
        self.assertEqual(True,
                         writing._create_virkning(self.from1, self.to1,
                                                  to_included=True)[
                             'to_included'],
                         'to_included should be true')

    def test_should_set_from_and_to_to_minus_and_plus_infinity(self):
        expected_virkning = {
            'from': '-infinity',
            'from_included': False,
            'to': 'infinity',
            'to_included': False
        }
        actual_virkning = writing._create_virkning('-infinity', 'infinity')
        self.assertEqual(expected_virkning, actual_virkning)

    # TODO: Should throw exception if to <= from
