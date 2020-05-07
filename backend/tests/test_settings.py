# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from mora import settings

from tests import util


class TestSettings(util.TestCase):
    def test_dict_key_intersection(self):
        d1 = {
            'config1': {
                'deprecated': 123,
            },
            'config3': 999
        }
        d2 = {
            'config1': {
                'deprecated': 123,
                'not_deprecated': 456
            },
            'config2': 789
        }

        expected = {
            'config1': {
                'deprecated': 123
            }
        }

        actual = settings.dict_key_intersection(d1, d2)

        self.assertEqual(expected, actual)

    def test_dict_key_intersection_empty_d1(self):

        d1 = {}
        d2 = {'whatever': 123}

        actual = settings.dict_key_intersection(d1, d2)

        self.assertEqual({}, actual)

    def test_dict_key_intersection_empty_d2(self):
        d1 = {'whatever': 123}
        d2 = {}

        actual = settings.dict_key_intersection(d1, d2)

        self.assertEqual({}, actual)

    def test_dict_key_difference(self):
        d1 = {
            'config1': {
                'valid': 123,
            },
            'config2': 456,
            'config3': {
                'valid2': 654312,
            }
        }
        d2 = {
            'config2': 456,
            'config3': {
                'valid2': 654312,
                'invalid': 789,
                'invalid2': {
                    'invalid3': 123456
                }
            }
        }

        expected = {
            'config3': {
                'invalid': 789,
                'invalid2': {
                    'invalid3': 123456
                }
            }
        }

        actual = settings.dict_key_difference(d1, d2)

        self.assertEqual(expected, actual)

    def test_dict_key_difference_empty_d1(self):
        d1 = {}
        d2 = {'whatever': 123}

        actual = settings.dict_key_difference(d1, d2)

        self.assertEqual(d2, actual)

    def test_dict_key_difference_empty_d2(self):
        d1 = {'whatever': 123}
        d2 = {}

        actual = settings.dict_key_difference(d1, d2)

        self.assertEqual(d1, actual)

    def test_update_dict(self):
        base = {
            "config1": {
                "setting1": 123,
                "setting2": 456
            },
            "config2": 789
        }
        new = {
            "config1": {
                "setting2": 999,
                "setting3": 111
            },
            "config2": 123,
            "config3": 123456

        }

        settings.update_dict(base, new)

        expected = {
            "config1": {
                "setting1": 123,
                "setting2": 999,
                "setting3": 111
            },
            "config2": 123,
            "config3": 123456
        }

        self.assertEqual(expected, base)
