# -- coding: utf-8 --

import unittest

from os2mo_data_import.data_types import Organisation

class TestOrganisation(unittest.TestCase):

    def test_attribute_validity(self):

        org = Organisation(
            name="ACME",
            date_from="1970-01-01",
            create_defaults=False
        )

        expected = {
            "from": "1970-01-01",
            "to": "infinity"
        }

        self.assertEqual(expected, org.validity)

    def test_auto_generated_user_key(self):

        org = Organisation(
            name="ACME",
            date_from="1970-01-01",
            create_defaults=False
        )

        self.assertEqual("ACME", org.user_key)

    def test_import_user_key(self):

        org = Organisation(
            name="ACME",
            user_key="B10D0D65-5779-4172-85E6-A64C2F6C8C02",
            create_defaults=False
        )

        self.assertEqual("B10D0D65-5779-4172-85E6-A64C2F6C8C02", org.user_key)

    def test_export_organisation(self):
        org = Organisation(
            uuid="3E89B0DB-5F27-41C1-8682-CF1292F1BE41",
            name="ACME",
            user_key="B10D0D65-5779-4172-85E6-A64C2F6C8C02",
            date_from="1986-01-02",
            create_defaults=False
        )

        export_data = org.export()

        expected = {
            'data': {
                "brugervendtnoegle": "B10D0D65-5779-4172-85E6-A64C2F6C8C02",
                "organisationsnavn": "ACME"
            },
            "municipality_code": 999,
            "uuid": "3E89B0DB-5F27-41C1-8682-CF1292F1BE41",
            "validity": {
                "from": "1986-01-02",
                "to": "infinity"
            }
        }

        self.assertEqual(expected, export_data)
