# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from copy import deepcopy

import pytest
from starlette.status import HTTP_200_OK
from starlette.status import HTTP_201_CREATED
from starlette.status import HTTP_400_BAD_REQUEST
from starlette.status import HTTP_403_FORBIDDEN

import tests.cases
from mora.auth.keycloak.oidc import auth
from mora.config import Settings
from mora.mapping import ADMIN
from mora.mapping import OWNER
from mora.mapping import PERSON
from mora.mapping import UUID
from tests.test_integration_rbac import mock_auth
from tests.util import jsonfile_to_dict
from tests.util import override_config

# Users
ANDERS_AND = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
FEDTMULE = "6ee24785-ee9a-4502-81c2-7697009c9053"
LIS_JENSEN = "7626ad64-327d-481f-8b32-36c78eb12f8c"
ERIK_SMIDT_HANSEN = "236e0a78-11a0-4ed9-8545-6286bb8611c7"

# URLs
URL_CREATE_DETAIL = "/service/details/create"
URL_EDIT_DETAIL = "/service/details/edit"
URL_TERMINATE_DETAIL = "/service/details/terminate"


class TestCommon(tests.cases.LoRATestCase):
    def setUp(self):
        super().setUp()
        self.create_owner_payload = jsonfile_to_dict(
            "tests/fixtures/rbac/create_employee_owner.json"
        )
        self.create_owner_payload[0][OWNER][UUID] = ANDERS_AND
        self.create_owner_payload[0][PERSON][UUID] = LIS_JENSEN

        # Use an admin user while setting up the test fixtures
        self.app.dependency_overrides[auth] = mock_auth(ADMIN, FEDTMULE)

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.create_owner_payload,
            status_code=HTTP_201_CREATED,
        )

        # Set the user back to a normal user, i.e. Bruce Lee
        self.app.dependency_overrides[auth] = mock_auth()


@pytest.mark.usefixtures("load_fixture_data_with_reset")
class TestCreateEmployee(tests.cases.LoRATestCase):
    def setUp(self):
        super().setUp()
        self.create_employee_url = "/service/e/create"

        self.create_employee_payload = {
            "name": "Mickey Mouse",
            "nickname_givenname": "",
            "cpr_no": "1111111111",
            "org": {
                "name": "Aarhus Universitet",
                "user_key": "AU",
                "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
            },
            "details": [],
        }

    @pytest.mark.parametrize(
        "role,userid,status_code",
        [
            (None, None, HTTP_403_FORBIDDEN),
            (OWNER, ANDERS_AND, HTTP_403_FORBIDDEN),
            (ADMIN, ANDERS_AND, HTTP_201_CREATED),
        ],
    )
    @override_config(Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_create_employee(self, role: str, userid: str, status_code: int):
        """
        Test of write access for the following cases:
        1) Normal user (no roles set)
        2) User with owner role
        3) User with the admin role

        :param role: the role of the user
        :param userid: the UUID of the user
        :param status_code: the expected HTTP status code
        """
        self.app.dependency_overrides[auth] = mock_auth(role, userid)
        self.assertRequest(
            self.create_employee_url,
            json=self.create_employee_payload,
            status_code=status_code,
        )


@pytest.mark.usefixtures("load_fixture_data_with_reset")
class TestCreateEmployeeDetailViaEmployee(TestCommon):

    # The "create details" endpoint is used for creating creating addresses,
    # it-systems, leaves and owners

    def setUp(self):
        super().setUp()

        # Payload for creating detail (phone number) on employee
        self.create_detail_payload = jsonfile_to_dict(
            "tests/fixtures/rbac/create_employee_detail_phone.json"
        )
        self.create_detail_payload[0][PERSON][UUID] = LIS_JENSEN
        self.create_it_system_payload = [
            {
                "type": "it",
                "user_key": "AD",
                "person": {"uuid": LIS_JENSEN},
                "itsystem": {"uuid": "59c135c9-2b15-41cc-97c8-b5dff7180beb"},
                "org": {
                    "name": "Aarhus Universitet",
                    "user_key": "AU",
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                },
                "validity": {"from": "2021-08-11", "to": None},
            }
        ]

    @pytest.mark.parametrize(
        "role,userid,status_code",
        [
            (None, None, HTTP_403_FORBIDDEN),
            (OWNER, FEDTMULE, HTTP_403_FORBIDDEN),
            (OWNER, ANDERS_AND, HTTP_201_CREATED),
            (ADMIN, FEDTMULE, HTTP_201_CREATED),
        ],
    )
    @override_config(Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_creating_detail_address(self, role: str, userid: str, status_code: int):
        """
        Test of write access for the following cases:
        1) Normal user (no roles set)
        2) User with the owner role, but not owner of the relevant entity
        3) User with the owner role and owner of the relative entity
        4) User with the admin role

        :param role: the role of the user
        :param userid: the UUID of the user
        :param status_code: the expected HTTP status code
        """
        self.app.dependency_overrides[auth] = mock_auth(role, userid)

        self.assertRequest(
            URL_CREATE_DETAIL, json=self.create_detail_payload, status_code=status_code
        )

    @override_config(Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_201_when_creating_it_system_detail_as_owner_of_employee(self):
        # Use user "Anders And" (who owns the employee)
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.create_it_system_payload,
            status_code=HTTP_201_CREATED,
        )

    @override_config(Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_201_when_creating_multiple_it_system_details_as_owner_of_employee(self):
        # Use user "Anders And" (who owns the employee)
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

        self.create_it_system_payload.append(self.create_it_system_payload[0])

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.create_it_system_payload,
            status_code=HTTP_201_CREATED,
        )


@pytest.mark.usefixtures("load_fixture_data_with_reset")
class TestCreateEmployeeDetailViaOrgUnit(tests.cases.LoRATestCase):
    """
    When creating employee details in the frontend some details actually
    resides under an org unit, e.g. employment, role, association,...
    A selection of these details are tested here (with respect to creating
    details)
    """

    def setUp(self) -> None:
        super().setUp()
        self.payload = jsonfile_to_dict(
            "tests/fixtures/rbac/create_employee_detail.json"
        )
        self.payload[0]["person"]["uuid"] = LIS_JENSEN

        self.create_multiple_associations = jsonfile_to_dict(
            "tests/fixtures/rbac/create_multiple_associations.json"
        )

        create_employment_payload = deepcopy(self.payload)
        create_employment_payload[0]["type"] = "engagement"
        create_employment_payload[0]["job_function"] = {
            "uuid": "f42dd694-f1fd-42a6-8a97-38777b73adc4",
            "name": "Bogopsætter",
            "user_key": "Bogopsætter",
            "example": None,
            "scope": None,
            "owner": None,
        }
        create_employment_payload[0]["engagement_type"] = {
            "uuid": "06f95678-166a-455a-a2ab-121a8d92ea23",
            "name": "Ansat",
            "user_key": "ansat",
            "example": None,
            "scope": None,
            "owner": None,
        }

        self.create_employment_payload = create_employment_payload

    @pytest.mark.parametrize(
        "role,userid,status_code",
        [(OWNER, ANDERS_AND, HTTP_201_CREATED), (OWNER, FEDTMULE, HTTP_403_FORBIDDEN)],
    )
    @override_config(Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_create_employment(self, role: str, userid: str, status_code: int):
        """
        Test of write access for the following cases:
        1) User with the owner role, but not owner of the relevant entity
        2) User with the owner role and owner of the relative entity

        :param role: the role of the user
        :param userid: the UUID of the user
        :param status_code: the expected HTTP status code
        """
        self.app.dependency_overrides[auth] = mock_auth(role, userid)

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.create_employment_payload,
            status_code=status_code,
        )

    @override_config(Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_create_multiple_employments_owns_one_unit_but_not_the_other(self):
        # Use user "Anders And" (who owns one unit but not the other)
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

        payload = jsonfile_to_dict(
            "tests/fixtures/rbac/create_multiple_employments.json"
        )

        self.assertRequest(
            URL_CREATE_DETAIL, json=payload, status_code=HTTP_403_FORBIDDEN
        )

    @override_config(Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_create_multiple_employments_owns_all_units(self):
        # Use user "Anders And" (who owns all units)
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)
        self.create_employment_payload.append(self.create_employment_payload[0])

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.create_employment_payload,
            status_code=HTTP_201_CREATED,
        )

    @override_config(Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_create_multiple_associations_owns_one_unit_but_not_the_other(self):
        # Use user "Anders And" (who owns one unit but not the other)
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.create_multiple_associations,
            status_code=HTTP_403_FORBIDDEN,
        )

    @override_config(Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_create_multiple_associations_owns_all_units(self):
        # Use user "Anders And" (who owns all units)
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

        self.create_multiple_associations[1] = self.create_multiple_associations[0]

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.create_multiple_associations,
            status_code=HTTP_201_CREATED,
        )

    @pytest.mark.parametrize(
        "role,userid,status_code",
        [(OWNER, ANDERS_AND, HTTP_201_CREATED), (OWNER, FEDTMULE, HTTP_403_FORBIDDEN)],
    )
    @override_config(Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_create_role(self, role: str, userid: str, status_code: int):
        """
        Test of write access for the following cases:
        1) User with the owner role, but not owner of the relevant entity
        2) User with the owner role and owner of the relative entity

        :param role: the role of the user
        :param userid: the UUID of the user
        :param status_code: the expected HTTP status code
        """

        self.app.dependency_overrides[auth] = mock_auth(role, userid)

        self.payload[0]["type"] = "role"
        self.payload[0]["role_type"] = {
            "uuid": "0fa6073f-32c0-4f82-865f-adb622ca0b04",
            "name": "Tillidsrepræsentant",
            "user_key": "Tillidsrepræsentant",
            "example": None,
            "scope": None,
            "owner": None,
        }

        self.assertRequest(
            URL_CREATE_DETAIL, json=self.payload, status_code=status_code
        )

    @pytest.mark.parametrize(
        "role,userid,status_code",
        [(OWNER, ANDERS_AND, HTTP_201_CREATED), (OWNER, FEDTMULE, HTTP_403_FORBIDDEN)],
    )
    @override_config(Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_create_association(self, role: str, userid: str, status_code: int):
        """
        Test of write access for the following cases:
        1) User with the owner role, but not owner of the relevant entity
        2) User with the owner role and owner of the relative entity

        :param role: the role of the user
        :param userid: the UUID of the user
        :param status_code: the expected HTTP status code
        """
        self.app.dependency_overrides[auth] = mock_auth(role, userid)

        self.payload[0]["type"] = "association"
        self.payload[0]["association_type"] = {
            "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
            "name": "Medlem",
            "user_key": "medl",
            "example": None,
            "scope": None,
            "owner": None,
        }

        self.assertRequest(
            URL_CREATE_DETAIL, json=self.payload, status_code=status_code
        )

    @pytest.mark.parametrize(
        "role,userid,status_code",
        [(OWNER, ANDERS_AND, HTTP_201_CREATED), (OWNER, FEDTMULE, HTTP_403_FORBIDDEN)],
    )
    @override_config(Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_create_manager(self, role: str, userid: str, status_code: int):
        """
        Test of write access for the following cases:
        1) User with the owner role, but not owner of the relevant entity
        2) User with the owner role and owner of the relative entity

        :param role: the role of the user
        :param userid: the UUID of the user
        :param status_code: the expected HTTP status code
        """
        self.app.dependency_overrides[auth] = mock_auth(role, userid)

        self.payload[0]["type"] = "manager"
        self.payload[0]["manager_type"] = {
            "uuid": "0d72900a-22a4-4390-a01e-fd65d0e0999d",
            "name": "Direktør",
            "user_key": "Direktør",
            "example": None,
            "scope": None,
            "owner": None,
        }
        self.payload[0]["manager_level"] = {
            "uuid": "3c791935-2cfa-46b5-a12e-66f7f54e70fe",
            "name": "Niveau 1",
            "user_key": "Niveau1",
            "example": None,
            "scope": None,
            "owner": None,
        }
        self.payload[0]["responsibility"] = [
            {
                "uuid": "93ea44f9-127c-4465-a34c-77d149e3e928",
                "name": "Beredskabsledelse",
                "user_key": "Beredskabsledelse",
                "example": None,
                "scope": None,
                "owner": None,
            }
        ]

        self.assertRequest(
            URL_CREATE_DETAIL, json=self.payload, status_code=status_code
        )

    @override_config(Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_object_types_in_list_must_be_identical(self):
        # Use user "Anders And" (who owns all units)
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

        self.create_multiple_associations[1] = deepcopy(
            self.create_multiple_associations[0]
        )

        self.create_multiple_associations[1]["type"] = "address"

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.create_multiple_associations,
            status_code=HTTP_400_BAD_REQUEST,
        )


@pytest.mark.usefixtures("load_fixture_data_with_reset")
class TestEditEmployeeDetail(TestCommon):
    def setUp(self) -> None:
        super().setUp()

        self.payload_edit_address = jsonfile_to_dict(
            "tests/fixtures/rbac/edit_address.json"
        )

        self.payload_edit_employment = jsonfile_to_dict(
            "tests/fixtures/rbac/edit_employment.json"
        )

        self.payload_edit_role = jsonfile_to_dict("tests/fixtures/rbac/edit_role.json")

        self.payload_edit_association = jsonfile_to_dict(
            "tests/fixtures/rbac/edit_association.json"
        )

        self.payload_edit_manager = jsonfile_to_dict(
            "tests/fixtures/rbac/edit_manager.json"
        )

        # Let Anders And be the owner of Fedtmule

        # Use an admin user while setting up the test fixtures
        self.app.dependency_overrides[auth] = mock_auth(ADMIN, ANDERS_AND)

        self.create_owner_payload[0]["person"]["uuid"] = FEDTMULE

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.create_owner_payload,
            status_code=HTTP_201_CREATED,
        )

        # Let Anders And be the owner of Erik Smidt Hansen

        # Use an admin user while setting up the test fixtures
        self.app.dependency_overrides[auth] = mock_auth(ADMIN, ANDERS_AND)

        self.create_owner_payload[0]["person"]["uuid"] = ERIK_SMIDT_HANSEN

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.create_owner_payload,
            status_code=HTTP_201_CREATED,
        )

        # Set the user back to a normal user, i.e. Bruce Lee
        self.app.dependency_overrides[auth] = mock_auth()

    @pytest.mark.parametrize(
        "role,userid,status_code",
        [
            (None, None, HTTP_403_FORBIDDEN),
            (OWNER, FEDTMULE, HTTP_403_FORBIDDEN),
            (OWNER, ANDERS_AND, HTTP_200_OK),
            (ADMIN, FEDTMULE, HTTP_200_OK),
        ],
    )
    @override_config(Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_edit_address(self, role: str, userid: str, status_code: int):
        """
        Test of write access for the following cases:
        1) Normal user (no roles set)
        2) User with the owner role, but not owner of the relevant entity
        3) User with the owner role and owner of the relative entity
        4) User with the admin role

        :param role: the role of the user
        :param userid: the UUID of the user
        :param status_code: the expected HTTP status code
        """
        self.app.dependency_overrides[auth] = mock_auth(role, userid)

        self.assertRequest(
            URL_EDIT_DETAIL, json=self.payload_edit_address, status_code=status_code
        )

    @pytest.mark.parametrize(
        "role,userid,status_code",
        [
            (None, None, HTTP_403_FORBIDDEN),
            (OWNER, FEDTMULE, HTTP_403_FORBIDDEN),
            (OWNER, ANDERS_AND, HTTP_200_OK),
            (ADMIN, FEDTMULE, HTTP_200_OK),
        ],
    )
    @override_config(Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_edit_employment(self, role: str, userid: str, status_code: int):
        """
        Test of write access for the following cases:
        1) Normal user (no roles set)
        2) User with the owner role, but not owner of the relevant entity
        3) User with the owner role and owner of the relative entity
        4) User with the admin role

        :param role: the role of the user
        :param userid: the UUID of the user
        :param status_code: the expected HTTP status code
        """
        self.app.dependency_overrides[auth] = mock_auth(role, userid)

        self.assertRequest(
            URL_EDIT_DETAIL, json=self.payload_edit_employment, status_code=status_code
        )

    @pytest.mark.parametrize(
        "role,userid,status_code",
        [
            (OWNER, FEDTMULE, HTTP_403_FORBIDDEN),
            (OWNER, ANDERS_AND, HTTP_200_OK),
        ],
    )
    @override_config(Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_edit_role(self, role: str, userid: str, status_code: int):
        """
        Test of write access for the following cases:
        1) User with the owner role, but not owner of the relevant entity
        2) User with the owner role and owner of the relative entity

        :param role: the role of the user
        :param userid: the UUID of the user
        :param status_code: the expected HTTP status code
        """
        self.app.dependency_overrides[auth] = mock_auth(role, userid)

        self.assertRequest(
            URL_EDIT_DETAIL, json=self.payload_edit_role, status_code=status_code
        )

    @pytest.mark.parametrize(
        "role,userid,status_code",
        [
            (OWNER, FEDTMULE, HTTP_403_FORBIDDEN),
            (OWNER, ANDERS_AND, HTTP_200_OK),
        ],
    )
    @override_config(Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_edit_association(self, role: str, userid: str, status_code: int):
        """
        Test of write access for the following cases:
        1) User with the owner role, but not owner of the relevant entity
        2) User with the owner role and owner of the relative entity

        :param role: the role of the user
        :param userid: the UUID of the user
        :param status_code: the expected HTTP status code
        """
        self.app.dependency_overrides[auth] = mock_auth(role, userid)

        self.assertRequest(
            URL_EDIT_DETAIL, json=self.payload_edit_association, status_code=status_code
        )

    @pytest.mark.parametrize(
        "role,userid,status_code",
        [
            (OWNER, FEDTMULE, HTTP_403_FORBIDDEN),
            (OWNER, ANDERS_AND, HTTP_200_OK),
        ],
    )
    @override_config(Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_edit_manager(self, role: str, userid: str, status_code: int):
        """
        Test of write access for the following cases:
        1) User with the owner role, but not owner of the relevant entity
        2) User with the owner role and owner of the relative entity

        :param role: the role of the user
        :param userid: the UUID of the user
        :param status_code: the expected HTTP status code
        """
        self.app.dependency_overrides[auth] = mock_auth(role, userid)

        self.assertRequest(
            URL_EDIT_DETAIL, json=self.payload_edit_manager, status_code=status_code
        )


@pytest.mark.usefixtures("load_fixture_data_with_reset")
class TestMoveEmployment(tests.cases.LoRATestCase):
    def setUp(self) -> None:
        super().setUp()
        # Move Erik Smidt Hansen from hum to samf
        self.move_single_employment_payload = jsonfile_to_dict(
            "tests/fixtures/rbac/move_employment.json"
        )

        self.move_multiple_employments_payload = jsonfile_to_dict(
            "tests/fixtures/rbac/move_multiple_employments.json"
        )

    @pytest.mark.parametrize(
        "role,userid,status_code",
        [
            (OWNER, FEDTMULE, HTTP_403_FORBIDDEN),
            (OWNER, ANDERS_AND, HTTP_200_OK),
        ],
    )
    @override_config(Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_move_employment(self, role: str, userid: str, status_code: int):
        """
        Test of write access for the following cases:
        1) User with the owner role, but not owner of the relevant entity
        2) User with the owner role and owner of the relative entity

        :param role: the role of the user
        :param userid: the UUID of the user
        :param status_code: the expected HTTP status code
        """

        self.app.dependency_overrides[auth] = mock_auth(role, userid)

        self.assertRequest(
            URL_EDIT_DETAIL,
            json=self.move_single_employment_payload,
            status_code=status_code,
        )

    @override_config(Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_move_multiple_employments_as_non_owner_of_source_unit(self):
        self.app.dependency_overrides[auth] = mock_auth(OWNER, FEDTMULE)

        self.assertRequest(
            URL_EDIT_DETAIL,
            json=self.move_multiple_employments_payload,
            status_code=HTTP_403_FORBIDDEN,
        )


@pytest.mark.usefixtures("load_fixture_data_with_reset")
class TestTerminateDetail(TestCommon):
    def setUp(self) -> None:
        super().setUp()

        self.payload_terminate_address = {
            "type": "address",
            "uuid": "64ea02e2-8469-4c54-a523-3d46729e86a7",
            "validity": {"to": "2021-08-20"},
        }

        self.payload_terminate_employment = {
            "type": "engagement",
            "uuid": "301a906b-ef51-4d5c-9c77-386fb8410459",
            "validity": {"to": "2021-08-13"},
        }

        # Let Anders And be the owner of Fedtmule

        # Use an admin user while setting up the test fixtures
        self.app.dependency_overrides[auth] = mock_auth(ADMIN, ANDERS_AND)

        self.create_owner_payload[0]["person"]["uuid"] = FEDTMULE

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.create_owner_payload,
            status_code=HTTP_201_CREATED,
        )

        # Set the user back to a normal user, i.e. Bruce Lee
        self.app.dependency_overrides[auth] = mock_auth()

    @pytest.mark.parametrize(
        "role,userid,status_code",
        [
            (None, None, HTTP_403_FORBIDDEN),
            (OWNER, FEDTMULE, HTTP_403_FORBIDDEN),
            (OWNER, ANDERS_AND, HTTP_200_OK),
            (ADMIN, FEDTMULE, HTTP_200_OK),
        ],
    )
    @override_config(Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_terminate_address(self, role: str, userid: str, status_code: int):
        """
        Test of write access for the following cases:
        1) Normal user (no roles set)
        2) User with the owner role, but not owner of the relevant entity
        3) User with the owner role and owner of the relative entity
        4) User with the admin role

        :param role: the role of the user
        :param userid: the UUID of the user
        :param status_code: the expected HTTP status code
        """
        self.app.dependency_overrides[auth] = mock_auth(role, userid)

        self.assertRequest(
            URL_TERMINATE_DETAIL,
            json=self.payload_terminate_address,
            status_code=status_code,
        )

    @pytest.mark.parametrize(
        "role,userid,status_code",
        [
            (None, None, HTTP_403_FORBIDDEN),
            (OWNER, FEDTMULE, HTTP_403_FORBIDDEN),
            (OWNER, ANDERS_AND, HTTP_200_OK),
            (ADMIN, FEDTMULE, HTTP_200_OK),
        ],
    )
    @pytest.mark.slow_setup
    @pytest.mark.slow
    @override_config(Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_terminate_employment(self, role: str, userid: str, status_code: int):
        """
        Test of write access for the following cases:
        1) Normal user (no roles set)
        2) User with the owner role, but not owner of the relevant entity
        3) User with the owner role and owner of the relative entity
        4) User with the admin role

        :param role: the role of the user
        :param userid: the UUID of the user
        :param status_code: the expected HTTP status code
        """
        self.app.dependency_overrides[auth] = mock_auth(role, userid)

        self.assertRequest(
            URL_TERMINATE_DETAIL,
            json=self.payload_terminate_employment,
            status_code=status_code,
        )


@pytest.mark.usefixtures("load_fixture_data_with_reset")
class TestTerminateEmployee(TestCommon):
    def setUp(self) -> None:
        super().setUp()

        self.url_terminate_employee = f"/service/e/{LIS_JENSEN}/terminate"
        self.payload_terminate_employee = {"validity": {"to": "2021-08-17"}}

    @pytest.mark.parametrize(
        "role,userid,status_code",
        [
            (None, None, HTTP_403_FORBIDDEN),
            (OWNER, FEDTMULE, HTTP_403_FORBIDDEN),
            (OWNER, ANDERS_AND, HTTP_200_OK),
            (ADMIN, FEDTMULE, HTTP_200_OK),
        ],
    )
    @override_config(Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_terminate_employee(self, role: str, userid: str, status_code: int):
        """
        Test of write access for the following cases:
        1) Normal user (no roles set)
        2) User with the owner role, but not owner of the relevant entity
        3) User with the owner role and owner of the relative entity
        4) User with the admin role

        :param role: the role of the user
        :param userid: the UUID of the user
        :param status_code: the expected HTTP status code
        """
        self.app.dependency_overrides[auth] = mock_auth(role, userid)

        self.assertRequest(
            self.url_terminate_employee,
            json=self.payload_terminate_employee,
            status_code=status_code,
        )


@pytest.mark.usefixtures("load_fixture_data_with_reset")
class TestEmployeeLeave(TestCommon):
    def setUp(self) -> None:
        super().setUp()
        self.payload_leave = jsonfile_to_dict("tests/fixtures/rbac/leave.json")

        # Let Anders And be the owner of Erik Smidt Hansen

        # Use an admin user while setting up the test fixtures
        self.app.dependency_overrides[auth] = mock_auth(ADMIN, ANDERS_AND)

        self.create_owner_payload[0]["person"]["uuid"] = ERIK_SMIDT_HANSEN

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.create_owner_payload,
            status_code=HTTP_201_CREATED,
        )

        # Set the user back to a normal user, i.e. Bruce Lee
        self.app.dependency_overrides[auth] = mock_auth()

    @pytest.mark.parametrize(
        "role,userid,status_code",
        [
            (None, None, HTTP_403_FORBIDDEN),
            (OWNER, FEDTMULE, HTTP_403_FORBIDDEN),
            (OWNER, ANDERS_AND, HTTP_201_CREATED),
            (ADMIN, FEDTMULE, HTTP_201_CREATED),
        ],
    )
    @pytest.mark.slow
    @override_config(Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_employee_leave(self, role: str, userid: str, status_code: int):
        """
        Test of write access for the following cases:
        1) Normal user (no roles set)
        2) User with the owner role, but not owner of the relevant entity
        3) User with the owner role and owner of the relative entity
        4) User with the admin role

        :param role: the role of the user
        :param userid: the UUID of the user
        :param status_code: the expected HTTP status code
        """
        self.app.dependency_overrides[auth] = mock_auth(role, userid)

        self.assertRequest(
            URL_CREATE_DETAIL, json=self.payload_leave, status_code=status_code
        )
