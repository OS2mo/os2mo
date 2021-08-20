# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_403_FORBIDDEN
)

from mora.auth.keycloak.oidc import auth
from mora.config import Settings
from mora.mapping import (
    ADMIN,
    OWNER,
    PERSON,
    UUID
)
import tests.cases
from tests.util import jsonfile_to_dict
from tests.util import override_config
from tests.test_integration_rbac import mock_auth

# Users
ANDERS_AND = '53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
FEDTMULE = '6ee24785-ee9a-4502-81c2-7697009c9053'
LIS_JENSEN = '7626ad64-327d-481f-8b32-36c78eb12f8c'
ERIK_SMIDT_HANSEN = '236e0a78-11a0-4ed9-8545-6286bb8611c7'

# URLs
URL_CREATE_DETAIL = '/service/details/create'
URL_EDIT_DETAIL = '/service/details/edit'
URL_TERMINATE_DETAIL = '/service/details/terminate'


class TestCommon(tests.cases.LoRATestCase):

    def setUp(self):
        super().setUp()
        self.load_sample_structures()

        self.create_owner_payload = jsonfile_to_dict(
            'tests/fixtures/rbac/create_employee_owner.json'
        )
        self.create_owner_payload[0][OWNER][UUID] = ANDERS_AND
        self.create_owner_payload[0][PERSON][UUID] = LIS_JENSEN

        # Use an admin user while setting up the test fixtures
        self.app.dependency_overrides[auth] = mock_auth(ADMIN, FEDTMULE)

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.create_owner_payload,
            status_code=HTTP_201_CREATED
        )

        # Set the user back to a normal user, i.e. Bruce Lee
        self.app.dependency_overrides[auth] = mock_auth()


class TestCreateEmployee(tests.cases.LoRATestCase):

    def setUp(self):
        super().setUp()
        self.load_sample_structures()

        self.create_employee_url = '/service/e/create'

        self.create_employee_payload = {
            "name": "Mickey Mouse",
            "nickname_givenname": "",
            "cpr_no": "1111111111",
            "org": {
                "name": "Aarhus Universitet",
                "user_key": "AU",
                "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
            },
            "details": []
        }

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_403_for_normal_user(self):
        self.app.dependency_overrides[auth] = mock_auth()
        self.assertRequest(
            self.create_employee_url,
            json=self.create_employee_payload,
            status_code=HTTP_403_FORBIDDEN
        )

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_201_for_admin(self):
        self.app.dependency_overrides[auth] = mock_auth(ADMIN, ANDERS_AND)
        self.assertRequest(
            self.create_employee_url,
            json=self.create_employee_payload,
            status_code=HTTP_201_CREATED
        )


class TestCreateEmployeeDetailViaEmployee(TestCommon):

    # The "create details" endpoint is used for creating creating addresses,
    # it-systems, leaves and owners

    def setUp(self):
        super().setUp()

        # Payload for creating detail (phone number) on employee
        self.create_detail_payload = jsonfile_to_dict(
            'tests/fixtures/rbac/create_employee_detail_phone.json'
        )
        self.create_detail_payload[0][PERSON][UUID] = LIS_JENSEN

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_403_when_creating_detail_as_normal_user(self):
        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.create_detail_payload,
            status_code=HTTP_403_FORBIDDEN
        )

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_403_when_creating_detail_as_owner_of_different_employee(self):
        # Use user "Fedtmule" (who does not own the employee)
        self.app.dependency_overrides[auth] = mock_auth(OWNER, FEDTMULE)

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.create_detail_payload,
            status_code=HTTP_403_FORBIDDEN
        )

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_201_when_creating_address_detail_as_owner_of_employee(self):
        # Use user "Anders And" (who owns the employee)
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.create_detail_payload,
            status_code=HTTP_201_CREATED
        )

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_201_when_creating_it_system_detail_as_owner_of_employee(self):
        # Use user "Anders And" (who owns the employee)
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

        payload = [
            {
                "type": "it",
                "user_key": "AD",
                "person": {
                    "uuid": LIS_JENSEN
                },
                "itsystem": {
                    "uuid": "59c135c9-2b15-41cc-97c8-b5dff7180beb"
                },
                "org": {
                    "name": "Aarhus Universitet", "user_key": "AU",
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                },
                "validity": {
                    "from": "2021-08-11",
                    "to": None
                }
            }
        ]

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=payload,
            status_code=HTTP_201_CREATED
        )

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_201_when_creating_detail_as_admin(self):
        # Use user "Fedtmule" (who does not own the employee)
        self.app.dependency_overrides[auth] = mock_auth(ADMIN, FEDTMULE)

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.create_detail_payload,
            status_code=HTTP_201_CREATED
        )


class TestCreateEmployeeDetailViaOrgUnit(tests.cases.LoRATestCase):
    """
    When creating employee details in the frontend some details actually
    resides under an org unit, e.g. employment, role, association,...
    A selection of these details are tested here (with respect to creating
    details)
    """

    def setUp(self) -> None:
        super().setUp()
        self.load_sample_structures()
        self.payload = jsonfile_to_dict(
            'tests/fixtures/rbac/create_employee_detail.json'
        )
        self.payload[0]["person"]["uuid"] = LIS_JENSEN

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_create_employment(self):
        # Use user "Anders And" (who owns the unit)
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

        self.payload[0]['type'] = 'engagement'
        self.payload[0]['job_function'] = {
            "uuid": "f42dd694-f1fd-42a6-8a97-38777b73adc4",
            "name": "Bogopsætter",
            "user_key": "Bogopsætter",
            "example": None,
            "scope": None,
            "owner": None
        }
        self.payload[0]['engagement_type'] = {
            "uuid": "06f95678-166a-455a-a2ab-121a8d92ea23",
            "name": "Ansat",
            "user_key": "ansat",
            "example": None,
            "scope": None,
            "owner": None
        }

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.payload,
            status_code=HTTP_201_CREATED
        )

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_create_role(self):
        # Use user "Anders And" (who owns the unit)
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

        self.payload[0]['type'] = 'role'
        self.payload[0]['role_type'] = {
            "uuid": "0fa6073f-32c0-4f82-865f-adb622ca0b04",
            "name": "Tillidsrepræsentant",
            "user_key": "Tillidsrepræsentant",
            "example": None,
            "scope": None,
            "owner": None
        }

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.payload,
            status_code=HTTP_201_CREATED
        )

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_create_role_as_non_owner(self):
        # Use user "Anders And" (who owns the unit)
        self.app.dependency_overrides[auth] = mock_auth(OWNER, FEDTMULE)

        self.payload[0]['type'] = 'role'
        self.payload[0]['role_type'] = {
            "uuid": "0fa6073f-32c0-4f82-865f-adb622ca0b04",
            "name": "Tillidsrepræsentant",
            "user_key": "Tillidsrepræsentant",
            "example": None,
            "scope": None,
            "owner": None
        }

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.payload,
            status_code=HTTP_403_FORBIDDEN
        )


class TestEditEmployeeDetail(TestCommon):

    def setUp(self) -> None:
        super().setUp()

        self.payload_edit_address = jsonfile_to_dict(
            'tests/fixtures/rbac/edit_address.json'
        )

        self.payload_edit_employment = jsonfile_to_dict(
            'tests/fixtures/rbac/edit_employment.json'
        )
        # Let Anders And be the owner of Fedtmule

        # Use an admin user while setting up the test fixtures
        self.app.dependency_overrides[auth] = mock_auth(ADMIN, ANDERS_AND)

        self.create_owner_payload[0]['person']['uuid'] = FEDTMULE

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.create_owner_payload,
            status_code=HTTP_201_CREATED
        )

        # Let Anders And be the owner of Erik Smidt Hansen

        # Use an admin user while setting up the test fixtures
        self.app.dependency_overrides[auth] = mock_auth(ADMIN, ANDERS_AND)

        self.create_owner_payload[0]['person']['uuid'] = ERIK_SMIDT_HANSEN

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.create_owner_payload,
            status_code=HTTP_201_CREATED
        )

        # Set the user back to a normal user, i.e. Bruce Lee
        self.app.dependency_overrides[auth] = mock_auth()

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_edit_address_as_normal_user(self):
        self.app.dependency_overrides[auth] = mock_auth()

        self.assertRequest(
            URL_EDIT_DETAIL,
            json=self.payload_edit_address,
            status_code=HTTP_403_FORBIDDEN
        )

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_edit_address_as_owner_but_not_owner_of_the_user(self):
        self.app.dependency_overrides[auth] = mock_auth(OWNER, FEDTMULE)

        self.assertRequest(
            URL_EDIT_DETAIL,
            json=self.payload_edit_address,
            status_code=HTTP_403_FORBIDDEN
        )

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_edit_address_as_owner_of_user(self):
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

        self.assertRequest(
            URL_EDIT_DETAIL,
            json=self.payload_edit_address,
            status_code=HTTP_200_OK
        )

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_edit_address_as_admin(self):
        self.app.dependency_overrides[auth] = mock_auth(ADMIN, FEDTMULE)

        self.assertRequest(
            URL_EDIT_DETAIL,
            json=self.payload_edit_address,
            status_code=HTTP_200_OK
        )

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_edit_employment_as_normal_user(self):
        self.app.dependency_overrides[auth] = mock_auth()

        self.assertRequest(
            URL_EDIT_DETAIL,
            json=self.payload_edit_employment,
            status_code=HTTP_403_FORBIDDEN
        )

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_edit_employment_as_owner_but_not_owner_of_the_user(self):
        self.app.dependency_overrides[auth] = mock_auth(OWNER, FEDTMULE)

        self.assertRequest(
            URL_EDIT_DETAIL,
            json=self.payload_edit_employment,
            status_code=HTTP_403_FORBIDDEN
        )

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_edit_employment_as_owner_of_user(self):
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

        self.assertRequest(
            URL_EDIT_DETAIL,
            json=self.payload_edit_employment,
            status_code=HTTP_200_OK
        )

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_edit_employment_as_admin(self):
        self.app.dependency_overrides[auth] = mock_auth(ADMIN, FEDTMULE)

        self.assertRequest(
            URL_EDIT_DETAIL,
            json=self.payload_edit_employment,
            status_code=HTTP_200_OK
        )


class TestTerminateDetail(TestCommon):

    def setUp(self) -> None:
        super().setUp()

        self.payload_terminate_address = {
            "type": "address",
            "uuid": "64ea02e2-8469-4c54-a523-3d46729e86a7",
            "validity": {
                "to": "2021-08-20"
            }
        }

        self.payload_terminate_employment = {
            "type": "engagement",
            "uuid": "301a906b-ef51-4d5c-9c77-386fb8410459",
            "validity": {
                "to": "2021-08-13"
            }
        }

        # Let Anders And be the owner of Fedtmule

        # Use an admin user while setting up the test fixtures
        self.app.dependency_overrides[auth] = mock_auth(ADMIN, ANDERS_AND)

        self.create_owner_payload[0]['person']['uuid'] = FEDTMULE

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.create_owner_payload,
            status_code=HTTP_201_CREATED
        )

        # Set the user back to a normal user, i.e. Bruce Lee
        self.app.dependency_overrides[auth] = mock_auth()

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_terminate_address_as_normal_user(self):
        self.app.dependency_overrides[auth] = mock_auth()

        self.assertRequest(
            URL_TERMINATE_DETAIL,
            json=self.payload_terminate_address,
            status_code=HTTP_403_FORBIDDEN
        )

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_terminate_address_as_owner_but_not_owner_of_the_user(self):
        self.app.dependency_overrides[auth] = mock_auth(OWNER, FEDTMULE)

        self.assertRequest(
            URL_TERMINATE_DETAIL,
            json=self.payload_terminate_address,
            status_code=HTTP_403_FORBIDDEN
        )

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_terminate_address_as_owner_of_user(self):
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

        self.assertRequest(
            URL_TERMINATE_DETAIL,
            json=self.payload_terminate_address,
            status_code=HTTP_200_OK
        )

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_terminate_address_as_admin(self):
        self.app.dependency_overrides[auth] = mock_auth(ADMIN, FEDTMULE)

        self.assertRequest(
            URL_TERMINATE_DETAIL,
            json=self.payload_terminate_address,
            status_code=HTTP_200_OK
        )

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_terminate_employment_as_normal_user(self):
        self.app.dependency_overrides[auth] = mock_auth()

        self.assertRequest(
            URL_TERMINATE_DETAIL,
            json=self.payload_terminate_employment,
            status_code=HTTP_403_FORBIDDEN
        )

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_terminate_employment_as_owner_but_not_owner_of_the_user(self):
        self.app.dependency_overrides[auth] = mock_auth(OWNER, FEDTMULE)

        self.assertRequest(
            URL_TERMINATE_DETAIL,
            json=self.payload_terminate_employment,
            status_code=HTTP_403_FORBIDDEN
        )

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_terminate_employment_as_owner_of_user(self):
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

        self.assertRequest(
            URL_TERMINATE_DETAIL,
            json=self.payload_terminate_employment,
            status_code=HTTP_200_OK
        )

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_terminate_employment_as_admin(self):
        self.app.dependency_overrides[auth] = mock_auth(ADMIN, FEDTMULE)

        self.assertRequest(
            URL_TERMINATE_DETAIL,
            json=self.payload_terminate_employment,
            status_code=HTTP_200_OK
        )


class TestTerminateEmployee(TestCommon):

    def setUp(self) -> None:
        super().setUp()

        self.url_terminate_employee = f'/service/e/{LIS_JENSEN}/terminate'
        self.payload_terminate_employee = {
            "validity": {
                "to": "2021-08-17"
            }
        }

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_terminate_employee_as_normal_user(self):
        self.app.dependency_overrides[auth] = mock_auth()

        self.assertRequest(
            self.url_terminate_employee,
            json=self.payload_terminate_employee,
            status_code=HTTP_403_FORBIDDEN
        )

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_terminate_employee_as_owner_but_not_owner_of_the_user(self):
        self.app.dependency_overrides[auth] = mock_auth(OWNER, FEDTMULE)

        self.assertRequest(
            self.url_terminate_employee,
            json=self.payload_terminate_employee,
            status_code=HTTP_403_FORBIDDEN
        )

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_terminate_employee_as_owner_of_user(self):
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

        self.assertRequest(
            self.url_terminate_employee,
            json=self.payload_terminate_employee,
            status_code=HTTP_200_OK
        )

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_terminate_employee_as_admin(self):
        self.app.dependency_overrides[auth] = mock_auth(ADMIN, FEDTMULE)

        self.assertRequest(
            self.url_terminate_employee,
            json=self.payload_terminate_employee,
            status_code=HTTP_200_OK
        )


class TestEmployeeLeave(TestCommon):

    def setUp(self) -> None:
        super().setUp()
        self.payload_leave = jsonfile_to_dict(
            'tests/fixtures/rbac/leave.json'
        )

        # Let Anders And be the owner of Erik Smidt Hansen

        # Use an admin user while setting up the test fixtures
        self.app.dependency_overrides[auth] = mock_auth(ADMIN, ANDERS_AND)

        self.create_owner_payload[0]['person']['uuid'] = ERIK_SMIDT_HANSEN

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.create_owner_payload,
            status_code=HTTP_201_CREATED
        )

        # Set the user back to a normal user, i.e. Bruce Lee
        self.app.dependency_overrides[auth] = mock_auth()

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_employee_leave_as_normal_user(self):
        self.app.dependency_overrides[auth] = mock_auth()

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.payload_leave,
            status_code=HTTP_403_FORBIDDEN
        )

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_employee_leave_as_owner_but_not_owner_of_the_user(self):
        self.app.dependency_overrides[auth] = mock_auth(OWNER, FEDTMULE)

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.payload_leave,
            status_code=HTTP_403_FORBIDDEN
        )

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_employee_employee_as_owner_of_user(self):
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.payload_leave,
            status_code=HTTP_201_CREATED
        )

    @override_config(
        Settings(confdb_show_owner=True, keycloak_rbac_enabled=True))
    def test_terminate_employee_as_admin(self):
        self.app.dependency_overrides[auth] = mock_auth(ADMIN, FEDTMULE)

        self.assertRequest(
            URL_CREATE_DETAIL,
            json=self.payload_leave,
            status_code=HTTP_201_CREATED
        )
