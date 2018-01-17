#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from unittest import TestCase

from mora.converters import writing


class TestEnsureObjectEffectBounds(TestCase):
    maxDiff = None

    def test_times_are_inside_bounds(self):
        # Arrange
        old_from = '2013-01-01T00:00:00+00:00'
        old_to = '2014-01-01T00:00:00+00:00'
        new_from = '2013-01-01T00:00:00+00:00'
        new_to = '2015-01-01T00:00:00+00:00'

        original = {
            'test1': {
                'test2': [
                    {
                        'uuid': 'HEJ2',
                        'virkning': {
                            'from': '2013-01-01T00:00:00+00:00',
                            'to': '2014-01-01T00:00:00+00:00',
                            'from_included': True,
                            'to_included': False,
                        }
                    },
                    {
                        'uuid': 'HEJ1',
                        'virkning': {
                            'from': '2012-01-01T00:00:00+00:00',
                            'to': '2013-01-01T00:00:00+00:00',
                            'from_included': True,
                            'to_included': False,
                        }
                    },
                    {
                        'uuid': 'HEJ3',
                        'virkning': {
                            'from': '2014-01-01T00:00:00+00:00',
                            'to': '2015-01-01T00:00:00+00:00',
                            'from_included': True,
                            'to_included': False,
                        }
                    },
                ]
            }
        }

        payload = {
            'whatever': ['I should remain untouched, please'],
            'test1': {
                'no': ['Me too']
            },
            'note': 'NOTE'
        }

        paths = [
            ['test1', 'test2']
        ]

        expected_result = {
            'whatever': ['I should remain untouched, please'],
            'test1': {
                'no': ['Me too']
            },
            'note': 'NOTE'
        }

        # Act
        actual_result = writing._ensure_object_effect_bounds(new_from, new_to,
                                                             original,
                                                             payload, paths)

        # Assert
        self.assertEqual(expected_result, actual_result)

    def test_expanding_from_time(self):
        # Arrange
        old_from = '2012-01-01T00:00:00+00:00'
        old_to = '2014-01-01T00:00:00+00:00'
        new_from = '2010-01-01T00:00:00+00:00'
        new_to = '2014-01-01T00:00:00+00:00'

        original = {
            'test1': {
                'test2': [
                    {
                        'uuid': 'HEJ2',
                        'virkning': {
                            'from': '2013-01-01T00:00:00+00:00',
                            'to': '2014-01-01T00:00:00+00:00',
                            'from_included': True,
                            'to_included': False,
                        }
                    },
                    {
                        'uuid': 'HEJ1',
                        'virkning': {
                            'from': '2012-01-01T00:00:00+00:00',
                            'to': '2013-01-01T00:00:00+00:00',
                            'from_included': True,
                            'to_included': False,
                        }
                    },
                    {
                        'uuid': 'HEJ3',
                        'virkning': {
                            'from': '2014-01-01T00:00:00+00:00',
                            'to': '2015-01-01T00:00:00+00:00',
                            'from_included': True,
                            'to_included': False,
                        }
                    },
                ]
            }
        }

        payload = {
            'whatever': ['I should remain untouched, please'],
            'test1': {
                'no': ['Me too']
            },
            'note': 'NOTE'
        }

        paths = [
            ['test1', 'test2']
        ]

        expected_result = {
            'whatever': ['I should remain untouched, please'],
            'note': 'NOTE',
            'test1': {
                'no': [
                    'Me too'
                ],
                'test2': [
                    {
                        'uuid': 'HEJ1',
                        'virkning': {
                            'from': '2010-01-01T00:00:00+00:00',
                            'to': '2013-01-01T00:00:00+00:00',
                            'from_included': True,
                            'to_included': False,
                        }
                    }
                ]
            }
        }

        # Act
        actual_result = writing._ensure_object_effect_bounds(new_from, new_to,
                                                             original,
                                                             payload, paths)

        # Assert
        self.assertEqual(expected_result, actual_result)

    def test_diminishing_from_time(self):
        # Arrange
        old_from = '2012-01-01T00:00:00+00:00'
        new_from = '2012-07-01T00:00:00+00:00'
        old_to = '2015-01-01T00:00:00+00:00'
        new_to = '2015-01-01T00:00:00+00:00'

        original = {
            'test1': {
                'test2': [
                    {
                        'uuid': 'HEJ2',
                        'virkning': {
                            'from': '2013-01-01T00:00:00+00:00',
                            'to': '2014-01-01T00:00:00+00:00',
                            'from_included': True,
                            'to_included': False,
                        }
                    },
                    {
                        'uuid': 'HEJ1',
                        'virkning': {
                            'from': '2012-01-01T00:00:00+00:00',
                            'to': '2013-01-01T00:00:00+00:00',
                            'from_included': True,
                            'to_included': False,
                        }
                    },
                    {
                        'uuid': 'HEJ3',
                        'virkning': {
                            'from': '2014-01-01T00:00:00+00:00',
                            'to': '2015-01-01T00:00:00+00:00',
                            'from_included': True,
                            'to_included': False,
                        }
                    },
                ]
            }
        }

        payload = {
            'whatever': ['I should remain untouched, please'],
            'test1': {
                'no': ['Me too']
            },
            'note': 'NOTE'
        }

        paths = [
            ['test1', 'test2']
        ]

        expected_result = {
            'whatever': ['I should remain untouched, please'],
            'note': 'NOTE',
            'test1': {
                'no': [
                    'Me too'
                ]
            }
        }

        # Act
        actual_result = writing._ensure_object_effect_bounds(new_from, new_to,
                                                             original,
                                                             payload, paths)

        # Assert
        self.assertEqual(expected_result, actual_result)

    def test_expanding_to_time(self):
        # Arrange
        old_from = '2012-01-01T00:00:00+00:00'
        old_to = '2015-01-01T00:00:00+00:00'
        new_from = '2012-01-01T00:00:00+00:00'
        new_to = '2017-01-01T00:00:00+00:00'

        original = {
            'test1': {
                'test2': [
                    {
                        'uuid': 'HEJ2',
                        'virkning': {
                            'from': '2013-01-01T00:00:00+00:00',
                            'to': '2014-01-01T00:00:00+00:00',
                            'from_included': True,
                            'to_included': False,
                        }
                    },
                    {
                        'uuid': 'HEJ1',
                        'virkning': {
                            'from': '2012-01-01T00:00:00+00:00',
                            'to': '2013-01-01T00:00:00+00:00',
                            'from_included': True,
                            'to_included': False,
                        }
                    },
                    {
                        'uuid': 'HEJ3',
                        'virkning': {
                            'from': '2014-01-01T00:00:00+00:00',
                            'to': '2015-01-01T00:00:00+00:00',
                            'from_included': True,
                            'to_included': False,
                        }
                    },
                ]
            }
        }

        payload = {
            'whatever': ['I should remain untouched, please'],
            'test1': {
                'no': ['Me too']
            },
            'note': 'NOTE'
        }

        paths = [
            ['test1', 'test2']
        ]

        expected_result = {
            'whatever': ['I should remain untouched, please'],
            'note': 'NOTE',
            'test1': {
                'no': [
                    'Me too'
                ],
                'test2': [
                    {
                        'uuid': 'HEJ3',
                        'virkning': {
                            'from': '2014-01-01T00:00:00+00:00',
                            'to': '2017-01-01T00:00:00+00:00',
                            'from_included': True,
                            'to_included': False,
                        }
                    },
                ]
            }
        }

        # Act
        actual_result = writing._ensure_object_effect_bounds(new_from, new_to,
                                                             original,
                                                             payload, paths)

        # Assert
        self.assertEqual(expected_result, actual_result)

    def test_diminishing_to_time(self):
        # Arrange
        old_from = '2012-01-01T00:00:00+00:00'
        new_from = '2012-01-01T00:00:00+00:00'
        old_to = '2015-01-01T00:00:00+00:00'
        new_to = '2014-07-01T00:00:00+00:00'

        original = {
            'test1': {
                'test2': [
                    {
                        'uuid': 'HEJ2',
                        'virkning': {
                            'from': '2013-01-01T00:00:00+00:00',
                            'to': '2014-01-01T00:00:00+00:00',
                            'from_included': True,
                            'to_included': False,
                        }
                    },
                    {
                        'uuid': 'HEJ1',
                        'virkning': {
                            'from': '2012-01-01T00:00:00+00:00',
                            'to': '2013-01-01T00:00:00+00:00',
                            'from_included': True,
                            'to_included': False,
                        }
                    },
                    {
                        'uuid': 'HEJ3',
                        'virkning': {
                            'from': '2014-01-01T00:00:00+00:00',
                            'to': '2015-01-01T00:00:00+00:00',
                            'from_included': True,
                            'to_included': False,
                        }
                    },
                ]
            }
        }

        payload = {
            'whatever': ['I should remain untouched, please'],
            'test1': {
                'no': ['Me too']
            },
            'note': 'NOTE'
        }

        paths = [
            ['test1', 'test2']
        ]

        expected_result = {
            'whatever': ['I should remain untouched, please'],
            'note': 'NOTE',
            'test1': {
                'no': [
                    'Me too'
                ]
            }
        }

        # Act
        actual_result = writing._ensure_object_effect_bounds(new_from, new_to,
                                                             original,
                                                             payload, paths)

        # Assert
        self.assertEqual(expected_result, actual_result)
