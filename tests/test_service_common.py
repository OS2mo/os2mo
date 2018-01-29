#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from unittest import TestCase

from mora.service.common import (FieldTuple, FieldTypes, get_obj_value,
                                 update_payload)


class TestClass(TestCase):
    maxDiff = None

    def test_get_obj_path(self):
        # Arrange
        obj = {
            'whatever': 'no',
            'test1': {
                'garbage': 'there is some stuff here already',
                'test2': ['something']
            }
        }

        path = ('test1', 'test2')

        expected_props = ['something']

        # Act
        actual_props = get_obj_value(obj, path)

        # Assert
        self.assertEqual(expected_props, actual_props)

    def test_update_payload_complex(self):
        # Arrange
        fields = [
            (
                FieldTuple(
                    ('test1', 'prop1'),
                    FieldTypes.ADAPTED_ZERO_TO_MANY,
                    lambda x: True,
                ),
                {
                    'uuid': '8525d022-e939-4d16-8378-2e46101a3a47',
                }
            ),
            (
                FieldTuple(
                    ('test1', 'prop2'),
                    FieldTypes.ZERO_TO_MANY,
                    lambda x: True,
                ),
                {
                    'uuid': '6995b5db-5e66-4479-82d8-67045663eb79',
                }
            ),
            (
                FieldTuple(
                    ('test2', 'prop3'),
                    FieldTypes.ZERO_TO_ONE,
                    lambda x: True,
                ),
                {
                    'uuid': '3251f325-a36f-4879-a150-2775cdc1b0fb',
                }
            )
        ]

        original = {
            'test1': {
                'prop1': [
                    {
                        'uuid': '1ebd2f10-df7b-42ca-93d9-3078a174c3f6',
                        'virkning': {
                            'from': '2016-01-01T00:00:00+00:00',
                            'to': '2018-01-01T00:00:00+00:00'
                        }
                    },
                    {
                        'uuid': '6563c93d-48da-4375-a106-b05343f97915',
                        'virkning': {
                            'from': '2018-01-01T00:00:00+00:00',
                            'to': '2020-01-01T00:00:00+00:00'
                        }
                    },
                ],
                'prop2': [
                    {
                        'uuid': 'eb936cf5-e72b-4aa9-9bd2-f773c462fa50',
                        'virkning': {
                            'from': '2016-01-01T00:00:00+00:00',
                            'to': '2020-01-01T00:00:00+00:00'
                        }
                    }
                ]
            },
            'test2': {
                'prop3': [
                    {
                        'uuid': 'ab9c5351-6448-4b6e-be02-eb3c16960884',
                        'virkning': {
                            'from': '2016-01-01T00:00:00+00:00',
                            'to': '2020-01-01T00:00:00+00:00'
                        }
                    }
                ]
            },
            'test3': {
                'prop4': [
                    {
                        'uuid': 'ab9c5351-6448-4b6e-be02-eb3c16960884',
                        'virkning': {
                            'from': '2016-01-01T00:00:00+00:00',
                            'to': '2020-01-01T00:00:00+00:00'
                        }
                    }
                ]
            }
        }

        expected_payload = {
            'test1': {
                'prop1': [
                    {
                        'uuid': '1ebd2f10-df7b-42ca-93d9-3078a174c3f6',
                        'virkning': {
                            'from': '2016-01-01T00:00:00+00:00',
                            'to': '2017-01-01T00:00:00+00:00'
                        }
                    },
                    {
                        'uuid': '8525d022-e939-4d16-8378-2e46101a3a47',
                        'virkning': {
                            'from': '2017-01-01T00:00:00+00:00',
                            'to': '2021-01-01T00:00:00+00:00'
                        }
                    }
                ],
                'prop2': [
                    {
                        'uuid': 'eb936cf5-e72b-4aa9-9bd2-f773c462fa50',
                        'virkning': {
                            'from': '2016-01-01T00:00:00+00:00',
                            'to': '2020-01-01T00:00:00+00:00'
                        }
                    },
                    {
                        'uuid': '6995b5db-5e66-4479-82d8-67045663eb79',
                        'virkning': {
                            'from': '2017-01-01T00:00:00+00:00',
                            'to': '2021-01-01T00:00:00+00:00'
                        }
                    }
                ]
            },
            'test2': {
                'prop3': [
                    {
                        'uuid': '3251f325-a36f-4879-a150-2775cdc1b0fb',
                        'virkning': {
                            'from': '2017-01-01T00:00:00+00:00',
                            'to': '2021-01-01T00:00:00+00:00'
                        }
                    }
                ]
            }
        }

        # Act
        actual_payload = update_payload(
            '2017-01-01T00:00:00+00:00',
            '2021-01-01T00:00:00+00:00',
            fields,
            original,
            {}
        )

        # Assert
        self.assertEqual(expected_payload, actual_payload)
