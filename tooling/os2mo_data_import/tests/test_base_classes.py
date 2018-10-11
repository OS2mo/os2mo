# -- coding: utf-8 --

import unittest

from os2mo_data_import.data_types import BaseMap


class TestBaseMap(unittest.TestCase):

    def setUp(self):
        self.BaseMap = BaseMap()

        self.identifier = "test_identifier"

        self.test_data = {
            "payload": True,
            "uuid": "1DFE4695-4238-4EFE-99E6-3924CB8CFBA2"
        }

        self.BaseMap.save(
            identifier=self.identifier,
            data=self.test_data
        )

    def test_existance_by_identifier(self):
        item_exists = self.BaseMap.check_if_exists(self.identifier)
        expected = True
        self.assertEqual(expected, item_exists)

    def test_get_data_by_identifier(self):
        return_data = self.BaseMap.get(self.identifier)
        self.assertEqual(self.test_data, return_data)

    def test_get_non_existent_item(self):
        # "Should raise KeyError"
        with self.assertRaises(KeyError):
            self.BaseMap.get("does not exist")

    def test_export_data(self):
        exported_data = self.BaseMap.export()

        expected = [
            (
                "test_identifier",
                {
                    "payload": True,
                    "uuid": "1DFE4695-4238-4EFE-99E6-3924CB8CFBA2"
                }
            )
        ]

        self.assertEqual(expected, exported_data)
