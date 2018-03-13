#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from unittest import TestCase

from mora.converters import writing


class TestMergeObj(TestCase):
    maxDiff = None

    def test_merge_obj_1(self):
        # New obj overlaps beginning and ending of originals
        # Arrange
        orig_objs = [
            {
                'uuid': 'whatever1',
                'virkning': {
                    'from': '2015-01-01T00:00:00+01:00',
                    'from_included': True,
                    'to': '2017-01-01T00:00:00+01:00',
                    'to_included': False,
                }
            },
            {
                'uuid': 'whatever2',
                'virkning': {
                    'from': '2017-01-01T00:00:00+01:00',
                    'from_included': True,
                    'to': '2019-01-01T00:00:00+01:00',
                    'to_included': False,
                }
            }
        ]

        new = {
            'uuid': 'whatever3',
            'virkning': {
                'from': '2016-01-01T00:00:00+01:00',
                'from_included': True,
                'to': '2018-01-01T00:00:00+01:00',
                'to_included': False,
            }
        }

        expected_result = [
            {
                'uuid': 'whatever1',
                'virkning': {
                    'from': '2015-01-01T00:00:00+01:00',
                    'from_included': True,
                    'to': '2016-01-01T00:00:00+01:00',
                    'to_included': False,
                }
            },
            {
                'uuid': 'whatever3',
                'virkning': {
                    'from': '2016-01-01T00:00:00+01:00',
                    'from_included': True,
                    'to': '2018-01-01T00:00:00+01:00',
                    'to_included': False,
                }
            },
            {
                'uuid': 'whatever2',
                'virkning': {
                    'from': '2018-01-01T00:00:00+01:00',
                    'from_included': True,
                    'to': '2019-01-01T00:00:00+01:00',
                    'to_included': False,
                }
            }
        ]

        # Act
        actual_result = writing._merge_obj_effects(orig_objs, new)

        actual_result = sorted(actual_result,
                               key=lambda x: x.get('virkning').get('from'))

        # Assert
        self.assertEqual(expected_result, actual_result)

    def test_merge_obj_2(self):
        # Original timespan completely contains new timespan
        # Arrange
        orig_objs = [
            {
                'uuid': 'whatever1',
                'virkning': {
                    'from': '2015-01-01T00:00:00+01:00',
                    'from_included': True,
                    'to': '2020-01-01T00:00:00+01:00',
                    'to_included': False,
                }
            }
        ]

        new = {
            'uuid': 'whatever3',
            'virkning': {
                'from': '2016-01-01T00:00:00+01:00',
                'from_included': True,
                'to': '2018-01-01T00:00:00+01:00',
                'to_included': False,
            }
        }

        expected_result = [
            {
                'uuid': 'whatever1',
                'virkning': {
                    'from': '2015-01-01T00:00:00+01:00',
                    'from_included': True,
                    'to': '2016-01-01T00:00:00+01:00',
                    'to_included': False,
                }
            },
            {
                'uuid': 'whatever3',
                'virkning': {
                    'from': '2016-01-01T00:00:00+01:00',
                    'from_included': True,
                    'to': '2018-01-01T00:00:00+01:00',
                    'to_included': False,
                }
            },
            {
                'uuid': 'whatever1',
                'virkning': {
                    'from': '2018-01-01T00:00:00+01:00',
                    'from_included': True,
                    'to': '2020-01-01T00:00:00+01:00',
                    'to_included': False,
                }
            }
        ]

        # Act
        actual_result = writing._merge_obj_effects(orig_objs, new)

        actual_result = sorted(actual_result,
                               key=lambda x: x.get('virkning').get('from'))

        # Assert
        self.assertEqual(expected_result, actual_result)

    def test_merge_obj_3(self):
        # New doesn't overlap with originals
        # Arrange
        orig_objs = [
            {
                'uuid': 'whatever1',
                'virkning': {
                    'from': '2015-01-01T00:00:00+01:00',
                    'from_included': True,
                    'to': '2016-01-01T00:00:00+01:00',
                    'to_included': False,
                }
            },
            {
                'uuid': 'whatever2',
                'virkning': {
                    'from': '2018-01-01T00:00:00+01:00',
                    'from_included': True,
                    'to': '2019-01-01T00:00:00+01:00',
                    'to_included': False,
                }
            }
        ]

        new = {
            'uuid': 'whatever3',
            'virkning': {
                'from': '2016-01-01T00:00:00+01:00',
                'from_included': True,
                'to': '2018-01-01T00:00:00+01:00',
                'to_included': False,
            }
        }

        expected_result = [
            {
                'uuid': 'whatever1',
                'virkning': {
                    'from': '2015-01-01T00:00:00+01:00',
                    'from_included': True,
                    'to': '2016-01-01T00:00:00+01:00',
                    'to_included': False,
                }
            },
            {
                'uuid': 'whatever3',
                'virkning': {
                    'from': '2016-01-01T00:00:00+01:00',
                    'from_included': True,
                    'to': '2018-01-01T00:00:00+01:00',
                    'to_included': False,
                }
            },
            {
                'uuid': 'whatever2',
                'virkning': {
                    'from': '2018-01-01T00:00:00+01:00',
                    'from_included': True,
                    'to': '2019-01-01T00:00:00+01:00',
                    'to_included': False,
                }
            }
        ]

        # Act
        actual_result = writing._merge_obj_effects(orig_objs, new)

        actual_result = sorted(actual_result,
                               key=lambda x: x.get('virkning').get('from'))

        # Assert
        self.assertEqual(expected_result, actual_result)

    def test_merge_obj_4(self):
        # New completely overlaps with old
        # Arrange
        orig_objs = [
            {
                'uuid': 'whatever1',
                'virkning': {
                    'from': '2015-01-01T00:00:00+01:00',
                    'from_included': True,
                    'to': '2016-01-01T00:00:00+01:00',
                    'to_included': False,
                }
            },
            {
                'uuid': 'whatever2',
                'virkning': {
                    'from': '2018-01-01T00:00:00+01:00',
                    'from_included': True,
                    'to': '2019-01-01T00:00:00+01:00',
                    'to_included': False,
                }
            }
        ]

        new = {
            'uuid': 'whatever3',
            'virkning': {
                'from': '2010-01-01T00:00:00+01:00',
                'from_included': True,
                'to': '2020-01-01T00:00:00+01:00',
                'to_included': False,
            }
        }

        expected_result = [
            {
                'uuid': 'whatever3',
                'virkning': {
                    'from': '2010-01-01T00:00:00+01:00',
                    'from_included': True,
                    'to': '2020-01-01T00:00:00+01:00',
                    'to_included': False,
                }
            }
        ]

        # Act
        actual_result = writing._merge_obj_effects(orig_objs, new)

        actual_result = sorted(actual_result,
                               key=lambda x: x.get('virkning').get('from'))

        # Assert
        self.assertEqual(expected_result, actual_result)

    def test_merge_obj_5(self):
        # Handle infinity
        # Arrange
        orig_objs = [
            {
                'uuid': 'whatever1',
                'virkning': {
                    'from': '2014-01-01T00:00:00+01:00',
                    'from_included': True,
                    'to': 'infinity',
                    'to_included': False,
                }
            }
        ]

        new = {
            'uuid': 'whatever2',
            'virkning': {
                'from': '2016-01-01T00:00:00+01:00',
                'from_included': True,
                'to': 'infinity',
                'to_included': False,
            }
        }

        expected_result = [
            {
                'uuid': 'whatever1',
                'virkning': {
                    'from': '2014-01-01T00:00:00+01:00',
                    'from_included': True,
                    'to': '2016-01-01T00:00:00+01:00',
                    'to_included': False,
                }
            },
            {
                'uuid': 'whatever2',
                'virkning': {
                    'from': '2016-01-01T00:00:00+01:00',
                    'from_included': True,
                    'to': 'infinity',
                    'to_included': False,
                }
            }
        ]

        # Act
        actual_result = writing._merge_obj_effects(orig_objs, new)

        actual_result = sorted(actual_result,
                               key=lambda x: x.get('virkning').get('from'))

        # Assert
        self.assertEqual(expected_result, actual_result)

    def test_merge_obj_6(self):
        # Handle -infinity
        # Arrange
        orig_objs = [
            {
                'uuid': 'whatever1',
                'virkning': {
                    'from': '-infinity',
                    'from_included': False,
                    'to': '2016-01-01T00:00:00+01:00',
                    'to_included': False,
                }
            }
        ]

        new = {
            'uuid': 'whatever2',
            'virkning': {
                'from': '-infinity',
                'from_included': False,
                'to': 'infinity',
                'to_included': False,
            }
        }

        expected_result = [
            {
                'uuid': 'whatever2',
                'virkning': {
                    'from': '-infinity',
                    'from_included': False,
                    'to': 'infinity',
                    'to_included': False,
                }
            }
        ]

        # Act
        actual_result = writing._merge_obj_effects(orig_objs, new)

        actual_result = sorted(actual_result,
                               key=lambda x: x.get('virkning').get('from'))

        # Assert
        self.assertEqual(expected_result, actual_result)
