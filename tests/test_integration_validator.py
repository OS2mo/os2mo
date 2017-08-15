#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from mora import validator
from tests import util


class TestIntegrationValidator(util.LoRATestCase):
    maxDiff = None

    # parent = samf, valid from 2017-01-01 to infinity
    ORG = '456362c4-0ee4-4e5e-a72c-751239745e62'
    PARENT = 'b688513d-11f7-4efc-b679-ab082a2055d0'

    def _expire_parent(self):
        # Expire the parent from 2018-01-01
        self.assertRequestResponse(
            '/o/%s/org-unit/%s?endDate=01-01-2018' % (self.ORG, self.PARENT),
            {
                'uuid': self.PARENT,
            },
            method='DELETE',
        )

    def test_should_return_true_when_interval_contained(self):
        """
        [------ super ------)
           [--- sub ---)
        """
        self.load_sample_structures()
        self._expire_parent()

        startdate = '01-02-2017'
        enddate = '01-06-2017'

        self.assertTrue(
            validator.is_date_range_valid(self.PARENT, startdate, enddate))

    def test_should_return_true_when_interval_contained2(self):
        """
        [------ super ------)
        [------ sub ---)
        """
        self.load_sample_structures()
        self._expire_parent()

        startdate = '01-01-2017'
        enddate = '01-06-2017'

        self.assertTrue(
            validator.is_date_range_valid(self.PARENT, startdate, enddate))

    def test_should_return_true_when_interval_contained3(self):
        """
        [------ super ------)
          [------ sub ------)
        """
        self.load_sample_structures()
        self._expire_parent()

        startdate = '01-02-2017'
        enddate = '01-01-2018'

        self.assertTrue(
            validator.is_date_range_valid(self.PARENT, startdate, enddate))

    def test_should_false_true_when_interval_not_contained1(self):
        """
          [---- super ------)
        [------ sub ---)
        """
        self.load_sample_structures()
        self._expire_parent()

        startdate = '01-01-2016'
        enddate = '01-06-2017'

        self.assertFalse(
            validator.is_date_range_valid(self.PARENT, startdate, enddate))

    def test_should_return_false_when_interval_not_contained2(self):
        """
        [------ super ------)
          [---- sub -----------)
        """
        self.load_sample_structures()
        self._expire_parent()

        startdate = '01-02-2017'
        enddate = '01-06-2019'

        self.assertFalse(
            validator.is_date_range_valid(self.PARENT, startdate, enddate))

    def test_should_return_false_when_interval_not_contained3(self):
        """
                                   [------ super ------)
        [---- sub -----------)
        """
        self.load_sample_structures()
        self._expire_parent()

        startdate = '01-02-2010'
        enddate = '01-06-2015'

        self.assertFalse(
            validator.is_date_range_valid(self.PARENT, startdate, enddate))
