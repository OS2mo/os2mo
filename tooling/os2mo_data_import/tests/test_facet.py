# -- coding: utf-8 --

import unittest

from os2mo_data_import.data_types import Facet


class TestFacet(unittest.TestCase):

    def setUp(self):

        self.Facet = Facet()
        self.Facet.add(identifier="test_facet")

    def test_if_exists(self):

        facet_exists = self.Facet.check_if_exists("test_facet")

        expected = True

        self.assertEqual(expected, facet_exists)

    def test_get_data_by_reference(self):

        facet_data = self.Facet.get("test_facet")

        expected = {
            "brugervendtnoegle": "test_facet"
        }

        self.assertEqual(expected, facet_data)

    def test_export_facet(self):

        facet_data = self.Facet.export()

        expected = [
            ("test_facet", {"brugervendtnoegle": "test_facet"})
        ]

        self.assertEqual(expected, facet_data)
