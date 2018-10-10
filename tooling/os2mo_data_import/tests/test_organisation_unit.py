# -- coding: utf-8 --

import unittest

from os2mo_data_import.data_types import OrganisationUnit


class TestOrganisationUnit(unittest.TestCase):

    def setUp(self):

        self.OrgUnit = OrganisationUnit()

    def test_adding_multipe_units_with_same_identifier(self):

        with self.assertRaises(AssertionError):

            self.OrgUnit.add(
                identifier="identical_unit",
                org_unit_type_ref="Custom",
                date_from="1980-01-01"
            )

            self.OrgUnit.add(
                identifier="identical_unit",
                org_unit_type_ref="Custom",
                date_from="1980-01-01"
            )

    def testing_data_payload(self):

        self.OrgUnit.add(
            identifier="test_unit",
            name=None,
            user_key="A0089744-ACC8-41DB-833C-155B66CF6C1A",
            org_unit_type_ref="Custom",
            parent_ref=None,
            date_from="1980-01-01"
        )

        data = self.OrgUnit.get_data("test_unit")

        expected = [
            ("name", "test_unit"),
            ("parent", None),
            ("org_unit_type", "Custom"),
            ("validity", {"from": "1980-01-01", "to": None}),
            ("user_key", "A0089744-ACC8-41DB-833C-155B66CF6C1A")
        ]

        self.assertEqual(expected, data)

    def test_optional_data_payload(self):
        self.OrgUnit.add(
            identifier="test_unit",
            org_unit_type_ref="Custom",
            date_from="1980-01-01"
        )

        self.OrgUnit.add_type_address(
            owner_ref="test_unit",
            value="11223344",
            address_type_ref="Custom",
            date_from="1980-01-01"
        )

        optional_data = self.OrgUnit.get_opt("test_unit")

        expected = [
            [
                ("type", "address"),
                ("address_type", "Custom"),
                ("validity", {"from": "1980-01-01", "to": None}),
                ("value", "11223344")
             ]
        ]

        self.assertEqual(expected, optional_data)

    def test_optional_data_missing_value(self):
        self.OrgUnit.add(
            identifier="test_unit",
            org_unit_type_ref="Custom",
            date_from="1980-01-01"
        )

        with self.assertRaises(ValueError):
            self.OrgUnit.add_type_address(
                owner_ref="test_unit",
                address_type_ref="Custom",
                date_from="1980-01-01"
            )
