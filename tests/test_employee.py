import copy
from unittest import TestCase

from mora.service.employee import (ensure_path_and_get_value, update_payload,
                                   PropTuple, PropTypes,
                                   merge_objs)


class TestClass(TestCase):
    maxDiff = None

    def test_get_and_set_path_new_path(self):
        # Arrange
        obj = {}
        original_obj = copy.deepcopy(obj)
        path = ('test1', 'test2')

        expected_props = []
        expected_obj = {
            'test1': {
                'test2': []
            }
        }

        # Act
        actual_obj, actual_props = ensure_path_and_get_value(obj, path)

        # Assert
        self.assertEqual(expected_props, actual_props)
        self.assertEqual(expected_obj, actual_obj)
        self.assertEqual(original_obj, obj)

    def test_get_and_set_path_existing_path(self):
        # Arrange
        obj = {
            'whatever': 'no',
            'test1': {
                'garbage': 'there is some stuff here already',
                'test2': ['something']
            }
        }

        original_obj = copy.deepcopy(obj)

        path = ('test1', 'test2')

        expected_props = ['something']
        expected_obj = {
            'whatever': 'no',
            'test1': {
                'garbage': 'there is some stuff here already',
                'test2': ['something']
            }
        }

        # Act
        actual_obj, actual_props = ensure_path_and_get_value(obj, path)

        # Assert
        self.assertEqual(expected_props, actual_props)
        self.assertEqual(expected_obj, actual_obj)
        self.assertEqual(original_obj, obj)

    def test_update_payload_complex(self):
        # Arrange
        fields = [
            (
                PropTuple(
                    ('test1', 'prop1'),
                    PropTypes.ADAPTED_ZERO_TO_MANY,
                    lambda x: True,
                ),
                {
                    'uuid': '8525d022-e939-4d16-8378-2e46101a3a47',
                }
            ),
            (
                PropTuple(
                    ('test1', 'prop2'),
                    PropTypes.ZERO_TO_MANY,
                    lambda x: True,
                ),
                {
                    'uuid': '6995b5db-5e66-4479-82d8-67045663eb79',
                }
            ),
            (
                PropTuple(
                    ('test2', 'prop3'),
                    PropTypes.ZERO_TO_ONE,
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

    def test_merge_objs(self):
        # Arrange
        obj1 = {
            'rels': {
                'rel1': [
                    {'whatever': 'val'}
                ],
                'rel2': [
                    {'whatever': 'val'}
                ]
            }
        }

        obj2 = {
            'attr': {
                'egenskaber': [{'bla1': 'val1'}, {'bla2': 'val2'}]
            },
            'rels': {
                'rel2': [
                    {'new': 'val'}
                ]
            }
        }

        expected_result = {
            'attr': {
                'egenskaber': [{'bla1': 'val1'}, {'bla2': 'val2'}]
            },
            'rels': {
                'rel1': [
                    {'whatever': 'val'}
                ],
                'rel2': [
                    {'new': 'val'},
                    {'whatever': 'val'},
                ]
            }
        }

        # Act
        # actual_result_1 = merge_objs(dict(obj1), dict(obj2))
        actual_result_2 = merge_objs(dict(obj2), dict(obj1))

        # Assert
        # self.assertEqual(expected_result, actual_result_1)
        self.assertEqual(expected_result, actual_result_2)
