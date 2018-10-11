# -- coding: utf-8 --

import unittest

from os2mo_data_import.data_types import Employee\


class TestEmployee(unittest.TestCase):

    def setUp(self):
        self.Employee = Employee()

        self.Employee.add(
            identifier="test_employee",
            cpr_no="0101805566",
            name="Susanne Chæf",
            user_key="5AD1E0B0-632C-4909-924E-2996F4F6961A",
        )

    def test_data_payload(self):
        data = self.Employee.get_data("test_employee")

        expected = [
            ("name", "Susanne Chæf"),
            ("cpr_no", "0101805566"),
            ("org", None),
            ("user_key", "5AD1E0B0-632C-4909-924E-2996F4F6961A")
        ]

        self.assertEqual(expected, data)

    def test_type_engagement(self):

        self.Employee.add_type_engagement(
            owner_ref="test_employee",
            org_unit_ref="test_org_unit",
            job_function_ref="medarbejder",
            engagement_type_ref="ansat",
            date_from="1986-01-01"
        )

        optional_data = self.Employee.get_opt("test_employee")

        expected = [
            [
                ("type", "engagement"),
                ("org_unit", "test_org_unit"),
                ("job_function", "medarbejder"),
                ("engagement_type", "ansat"),
                ("validity", {"from": "1986-01-01", "to": None})
             ]
        ]

        self.assertEqual(expected, optional_data)

    def test_type_association(self):

        self.Employee.add_type_association(
            owner_ref="test_employee",
            org_unit_ref="test_org_unit",
            job_function_ref="medarbejder",
            association_type_ref="ekstern konsulent",
            address_uuid="BF18EB2F-82BB-4856-88C9-40E2CF8D1E13",
            date_from="1986-01-01"
        )

        optional_data = self.Employee.get_opt("test_employee")

        expected = [
            [
                ("type", "association"),
                ("org_unit", "test_org_unit"),
                ("job_function", "medarbejder"),
                ("association_type", "ekstern konsulent"),
                ("validity", {"from": "1986-01-01", "to": None}),
                ("address", "BF18EB2F-82BB-4856-88C9-40E2CF8D1E13")
            ]
        ]

        self.assertEqual(expected, optional_data)

    def test_type_role(self):

        self.Employee.add_type_role(
            owner_ref="test_employee",
            org_unit_ref="test_org_unit",
            role_type_ref="nøgleansvarlig",
            date_from="1986-01-01"
        )

        optional_data = self.Employee.get_opt("test_employee")

        expected = [
            [
                ("type", "role"),
                ("org_unit", "test_org_unit"),
                ("role_type", "nøgleansvarlig"),
                ("validity", {"from": "1986-01-01", "to": None})
            ]
        ]

        self.assertEqual(expected, optional_data)

    def test_type_manager(self):

        self.Employee.add_type_manager(
            owner_ref="test_employee",
            org_unit_ref="test_org_unit",
            manager_type_ref="direktør",
            manager_level_ref="niveau 90",
            responsibility_list=["personaleansvar", "ledelse"],
            address_uuid="A6B5B631-0D49-46F3-8713-CE2F9E7EB7A0",
            date_from="1986-01-01"
        )

        optional_data = self.Employee.get_opt("test_employee")

        expected = [
            [
                ("type", "manager"),
                ("org_unit", "test_org_unit"),
                ("manager_type", "direktør"),
                ("manager_level", "niveau 90"),
                ("responsibility", ["personaleansvar", "ledelse"]),
                ("validity", {"from": "1986-01-01", "to": None}),
                ("address", "A6B5B631-0D49-46F3-8713-CE2F9E7EB7A0")
            ]
        ]

        self.assertEqual(expected, optional_data)

    def test_type_leave(self):

        self.Employee.add_type_leave(
            owner_ref="test_employee",
            leave_type_ref="sygeorglov",
            date_from="1986-01-01"
        )

        optional_data = self.Employee.get_opt("test_employee")

        expected = [
            [
                ("type", "leave"),
                ("leave_type", "sygeorglov"),
                ("validity", {"from": "1986-01-01", "to": None})
            ]
        ]

        self.assertEqual(expected, optional_data)

    def test_type_itsystem(self):

        self.Employee.add_type_itsystem(
            owner_ref="test_employee",
            user_key="sc123",
            itsystem_ref="os2mo",
            date_from="1986-01-01"
        )

        optional_data = self.Employee.get_opt("test_employee")

        expected = [
            [
                ("type", "it"),
                ("user_key", "sc123"),
                ("itsystem", "os2mo"),
                ("validity", {"from": "1986-01-01", "to": None})
            ]
        ]

        self.assertEqual(expected, optional_data)

    def test_type_address(self):
        self.Employee.add_type_address(
            owner_ref="test_employee",
            uuid="8807E3B5-6E5A-4434-BA56-9DADD26195AC",
            address_type_ref="Custom",
            date_from="1980-01-01"
        )

        optional_data = self.Employee.get_opt("test_employee")

        expected = [
            [
                ("type", "address"),
                ("address_type", "Custom"),
                ("validity", {"from": "1980-01-01", "to": None}),
                ("uuid", "8807E3B5-6E5A-4434-BA56-9DADD26195AC")
            ]
        ]

        self.assertEqual(expected, optional_data)
