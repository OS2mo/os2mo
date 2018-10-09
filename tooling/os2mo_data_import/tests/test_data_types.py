# -- coding: utf-8 --

import unittest

from os2mo_data_import.data_types import (
    BaseMap,
    Organisation,
    Facet,
    Klasse,
    Itsystem,
    OrganisationUnit,
    Employee
)


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


class TestItsystem(unittest.TestCase):

    def setUp(self):

        self.Itsystem = Itsystem()

        self.Itsystem.add(
            identifier="test_itsystem"
        )

    def test_autogenerated_name_and_user_key(self):

        itsystem = self.Itsystem.get("test_itsystem")

        self.assertTrue(
            itsystem["brugervendtnoegle"] == "test_itsystem" and
            itsystem["itsystemnavn"] == "test_itsystem"
        )


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
