#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import unittest

import freezegun

from mora.converters import writing
from mora import exceptions


class TestHelperFunctions(unittest.TestCase):
    maxDiff = None

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
            'name': 'Whatever',
            'primaer': True,
            'location': 'dummy1',
            'valid-from': 'dummy2',
            'valid-to': 'dummy3',
        }
        expected = {
            'address_uuid': 'uuid',
            'location': 'dummy1',
            'name': 'Whatever',
            'primary': True,
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
            'name': 'Whatever',
            'primaer': True,
            'valid-from': 'dummy2',
            'valid-to': 'dummy3',
        }
        expected = {
            'location': 'dummy1',
            'name': 'Whatever',
            'primary': True,
            'From': 'dummy2',
            'to': 'dummy3'
        }
        self.assertEqual(expected,
                         writing.create_update_kwargs(None, req))

    # Testing _create_payload function

    def test_should_append_props_correctly(self):
        payload = {
            'note': 'dummy note',
            'a': {
                'b': [
                    {
                        'c': 'dummy',
                        'virkning': {
                            'from': '2000-01-01',
                            'from_included': True,
                            'to': '2000-12-12',
                            'to_included': False,
                        }
                    }
                ]
            }
        }
        expected_output = {
            'note': 'changed dummy note',
            'a': {
                'b': [
                    {
                        'c': 'dummy',
                        'virkning': {
                            'from': '2000-01-01',
                            'from_included': True,
                            'to': '2000-12-12',
                            'to_included': False,
                        }
                    },
                    {
                        'c': 'dummy2',
                        'virkning': {
                            'from': '2000-01-01T00:00:00+01:00',
                            'from_included': True,
                            'to': '2000-12-12T00:00:00+01:00',
                            'to_included': False,
                        }
                    }
                ]
            }
        }
        props = {'c': 'dummy2'}
        actual_output = writing._create_payload('01-01-2000', '12-12-2000',
                                                ['a', 'b'],
                                                props,
                                                'changed dummy note',
                                                payload)
        self.assertEqual(expected_output, actual_output)

    @freezegun.freeze_time(tz_offset=+1)
    def test_should_add_more_payloads_correctly(self):
        obj_path = ['tilstande', 'organisationenhedgyldighed']
        props_active = {'gyldighed': 'Aktiv'}
        props_inactive = {'gyldighed': 'Inaktiv'}

        payload = writing._create_payload('-infinity', '01-01-2000', obj_path,
                                          props_inactive, 'Afslut enhed')

        self.assertEqual({
            'note': 'Afslut enhed',
            'tilstande': {
                'organisationenhedgyldighed': [
                    {
                        'gyldighed': 'Inaktiv',
                        'virkning': {
                            'from': '-infinity',
                            'from_included': False,
                            'to': '2000-01-01T00:00:00+01:00',
                            'to_included': False,
                        }
                    }
                ]
            }
        },
            payload
        )

        payload2 = writing._create_payload('01-01-2000', '01-02-2000',
                                           obj_path, props_active,
                                           'Afslut enhed', payload)

        self.assertEqual({
            'note': 'Afslut enhed',
            'tilstande': {
                'organisationenhedgyldighed': [
                    {
                        'gyldighed': 'Inaktiv',
                        'virkning': {
                            'from': '-infinity',
                            'from_included': False,
                            'to': '2000-01-01T00:00:00+01:00',
                            'to_included': False,
                        }
                    },
                    {
                        'gyldighed': 'Aktiv',
                        'virkning': {
                            'from': '2000-01-01T00:00:00+01:00',
                            'from_included': True,
                            'to': '2000-02-01T00:00:00+01:00',
                            'to_included': False,
                        }
                    }

                ]
            }
        },
            payload2
        )
