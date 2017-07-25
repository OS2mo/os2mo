#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import unittest

from mora.converters import writing
from mora import exceptions


class TestHelperFunctions(unittest.TestCase):

    # Testing _check_arguments function

    def test_should_raise_exception_if_arg_is_missing(self):
        mandatory_args = ['a']
        args_to_check = ['b', 'c']
        with self.assertRaises(exceptions.IllegalArgumentException):
            writing._check_arguments(mandatory_args, args_to_check)

    # Testing create_update_kwargs function

    def test_should_return_correct_kwargs_for_roletype_contact_channel(self):
        req = {
            'contact-channels': 'dummy',
            'location': None
        }
        expected = {
            'contact_channels': 'dummy'
        }
        self.assertEqual(expected,
                         writing.create_update_kwargs('contact-channel', req))

    def test_should_return_correct_kwargs_for_roletype_contact_channel2(self):
        # Location not present in the request here
        req = {
            'contact-channels': 'dummy',
        }
        expected = {}
        self.assertEqual(expected,
                         writing.create_update_kwargs('contact-channel', req))

    def test_should_return_correct_kwargs_for_roletype_location(self):
        req = {
            'uuid': 'uuid',
            'location': 'dummy1',
            'valid-from': 'dummy2',
            'valid-to': 'dummy3',
        }
        expected = {
            'address_uuid': 'uuid',
            'location': 'dummy1',
            'From': 'dummy2',
            'to': 'dummy3'
        }
        self.assertEqual(expected,
                         writing.create_update_kwargs('location', req))

    def test_should_raise_exception_when_roletype_unknown(self):
        with self.assertRaises(NotImplementedError):
            writing.create_update_kwargs('unknown', {})

    def test_should_return_correct_kwargs_for_roletype_None(self):
        req = {
            'location': 'dummy1',
            'valid-from': 'dummy2',
            'valid-to': 'dummy3',
        }
        expected = {
            'location': 'dummy1',
            'From': 'dummy2',
            'to': 'dummy3'
        }
        self.assertEqual(expected,
                         writing.create_update_kwargs(None, req))
