#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from unittest import TestCase

from mora.converters.writing import _inactivate_old_interval


class TestInactivateOldInterval(TestCase):
    maxDiff = None

    def test_inactivates_correctly_when_diminishing_bounds(self):
        # Arrange
        old_from = '2013-01-01T00:00:00+00:00'
        old_to = '2016-01-01T00:00:00+00:00'
        new_from = '2014-01-01T00:00:00+00:00'
        new_to = '2015-01-01T00:00:00+00:00'
        payload = {
            'whatever': ['Should remain untouched'],
            'note': 'NOTE'
        }
        path = ['hest', 'hestgyldighed']

        expected_result = {
            'whatever': ['Should remain untouched'],
            'hest': {
                'hestgyldighed': [
                    {
                        'gyldighed': 'Inaktiv',
                        'virkning': {
                            'from': '2013-01-01T00:00:00+00:00',
                            'to': '2014-01-01T00:00:00+00:00',
                            'from_included': True,
                            'to_included': False,
                        }
                    },
                    {
                        'gyldighed': 'Inaktiv',
                        'virkning': {
                            'from': '2015-01-01T00:00:00+00:00',
                            'to': '2016-01-01T00:00:00+00:00',
                            'from_included': True,
                            'to_included': False,
                        }
                    }
                ]
            },
            'note': 'NOTE'
        }

        # Act
        actual_result = _inactivate_old_interval(old_from, old_to, new_from,
                                                 new_to, payload, path)

        # Assert
        self.assertEqual(expected_result, actual_result)

    def test_does_not_inactivate_when_expanding_bounds(self):
        # Arrange
        old_from = '2014-01-01T00:00:00+00:00'
        old_to = '2015-01-01T00:00:00+00:00'
        new_from = '2013-01-01T00:00:00+00:00'
        new_to = '2016-01-01T00:00:00+00:00'
        payload = {
            'whatever': ['Should remain untouched'],
            'note': 'NOTE'
        }
        path = ['hest', 'hestgyldighed']

        expected_result = {
            'whatever': ['Should remain untouched'],
            'note': 'NOTE'
        }

        # Act
        actual_result = _inactivate_old_interval(old_from, old_to, new_from,
                                                 new_to, payload, path)

        # Assert
        self.assertEqual(expected_result, actual_result)

    def test_does_not_inactivate_when_bounds_do_not_move(self):
        # Arrange
        old_from = '2014-01-01T00:00:00+00:00'
        old_to = '2015-01-01T00:00:00+00:00'
        new_from = '2014-01-01T00:00:00+00:00'
        new_to = '2015-01-01T00:00:00+00:00'
        payload = {
            'whatever': ['Should remain untouched'],
            'note': 'NOTE'
        }
        path = ['hest', 'hestgyldighed']

        expected_result = {
            'whatever': ['Should remain untouched'],
            'note': 'NOTE'
        }

        # Act
        actual_result = _inactivate_old_interval(old_from, old_to, new_from,
                                                 new_to, payload, path)

        # Assert
        self.assertEqual(expected_result, actual_result)
