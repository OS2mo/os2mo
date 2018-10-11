# -- coding: utf-8 --

import unittest

from os2mo_data_import.data_types import Klasse


class TestKlasse(unittest.TestCase):

    def setUp(self):

        self.Klasse = Klasse()

    def test_export_none_type_values(self):

        self.Klasse.add(
            identifier="test_klasse",
            facet_type_ref="test_facet",
            user_key=None,
            description=None,
            example=None,
            scope=None,
            title=None
        )

        klasse_data = self.Klasse.get("test_klasse")

        expected = {
            "facet_type_ref": "test_facet",
            "data": {
                "brugervendtnoegle": "test_klasse"
            }
        }

        self.assertEqual(expected, klasse_data)

    def test_all_params_present(self):

        self.Klasse.add(
            identifier="test_klasse",
            facet_type_ref="test_facet",
            user_key="B0EEF465-6C5A-463B-9DAD-75EC5D9A4FFF",
            description="this is a placeholder",
            example="<UUID>",
            scope="CUSTOM",
            title="this is the displayed value"
        )

        klasse_data = self.Klasse.get("test_klasse")

        check_params = [
            "brugervendtnoegle",
            "beskrivelse",
            "eksempel",
            "omfang",
            "titel"
        ]

        params_missing = [
            param for param in check_params
            if param not in klasse_data["data"]
        ]

        self.assertFalse(params_missing)
