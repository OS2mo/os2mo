# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from copy import deepcopy
from datetime import datetime

import pytest
from parameterized import parameterized
from starlette.status import HTTP_200_OK
from starlette.status import HTTP_201_CREATED
from starlette.status import HTTP_400_BAD_REQUEST
from starlette.status import HTTP_403_FORBIDDEN

import tests.cases
from mora.auth.keycloak.models import Token
from mora.auth.keycloak.oidc import auth
from mora.config import Settings
from mora.mapping import ADMIN
from mora.mapping import OWNER
from tests import util

# Users
ANDERS_AND = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
FEDTMULE = "6ee24785-ee9a-4502-81c2-7697009c9053"

# Org units
ROOT_UNIT = "2874e1dc-85e6-4269-823a-e1125484dfd3"
HUM_UNIT = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
FILOSOFISK_INSTITUT = "85715fc7-925d-401b-822d-467eb4b163b6"


def mock_auth(role: str = None, user_uuid: str = None):
    """
    Create auth for a user with the given role (admin or owner) and the given
    user UUID
    """

    token = {
        "acr": "1",
        "allowed-origins": ["http://localhost:5001"],
        "azp": "vue",
        "email": "bruce@kung.fu",
        "email_verified": False,
        "exp": 1621779689,
        "family_name": "Lee",
        "given_name": "Bruce",
        "iat": 1621779389,
        "iss": "http://localhost:8081/auth/realms/mo",
        "jti": "25dbb58d-b3cb-4880-8b51-8b92ada4528a",
        "name": "Bruce Lee",
        "preferred_username": "bruce",
        "scope": "email profile",
        "session_state": "d94f8dc3-d930-49b3-a9dd-9cdc1893b86a",
        "sub": "c420894f-36ba-4cd5-b4f8-1b24bd8c53db",
        "typ": "Bearer",
        "uuid": "00000000-0000-0000-0000-000000000000",
    }

    if bool(role) ^ bool(user_uuid):
        raise AssertionError("Both of arguments should be set or not set")

    if role and user_uuid:
        token.update({"realm_access": {"roles": [role]}, "uuid": user_uuid})

    def fake_auth():
        return Token.parse_obj(token)

    return fake_auth


@pytest.mark.usefixtures("load_fixture_data_with_reset")
class TestCommon(tests.cases.LoRATestCase):
    def setUp(self):
        super().setUp()

        self.url_create = "/service/ou/create"
        self.url_create_detail = "/service/details/create"
        self.url_edit_detail = "/service/details/edit"
        self.url_terminate_detail = "/service/details/terminate"

        self.create_org_unit_payload = {
            "name": "Fake Corp",
            "time_planning": {
                "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
            },
            "parent": {"uuid": ROOT_UNIT},
            "org_unit_type": {"uuid": "ca76a441-6226-404f-88a9-31e02e420e52"},
            "org_unit_level": {"uuid": "0f015b67-f250-43bb-9160-043ec19fad48"},
            "org_unit_hierarchy": {"uuid": "12345678-abcd-abcd-1234-12345678abcd"},
            "details": [
                {
                    "type": "address",
                    "address_type": {
                        "example": "20304060",
                        "name": "Telefon",
                        "scope": "PHONE",
                        "user_key": "Telefon",
                        "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                    },
                    "org": {
                        "name": "Aarhus Universitet",
                        "user_key": "AU",
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                    },
                    "validity": {
                        "from": "2016-02-04",
                        "to": None,
                    },
                    "value": "11223344",
                },
                {
                    "type": "address",
                    "address_type": {
                        "example": "<UUID>",
                        "name": "Adresse",
                        "scope": "DAR",
                        "user_key": "Adresse",
                        "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed",
                    },
                    "org": {
                        "name": "Aarhus Universitet",
                        "user_key": "AU",
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                    },
                    "validity": {
                        "from": "2016-02-04",
                        "to": None,
                    },
                    "value": "44c532e1-f617-4174-b144-d37ce9fda2bd",
                },
            ],
            "validity": {
                "from": "2016-02-04",
                "to": None,
            },
        }

        self.create_owner_payload = [
            {
                "type": "owner",
                "owner": {
                    "givenname": "Anders",
                    "surname": "And",
                    "name": "Anders And",
                    "nickname_givenname": "Donald",
                    "nickname_surname": "Duck",
                    "nickname": "Donald Duck",
                    "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                    "seniority": None,
                    "cpr_no": "0906340000",
                    "org": {
                        "name": "Aarhus Universitet",
                        "user_key": "AU",
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                    },
                    "user_key": "andersand",
                },
                "org": {
                    "name": "Aarhus Universitet",
                    "user_key": "AU",
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                },
                "validity": {"from": "2021-08-03", "to": None},
                "org_unit": {"uuid": "<uuid>"},
            }
        ]

        # Payload for renaming Humanistisk Fakultet
        self.rename_payload = {
            "type": "org_unit",
            "data": {
                "name": "New name",
                "uuid": HUM_UNIT,
                "clamp": True,
                "validity": {"from": "2021-07-28"},
            },
        }

        # Use an admin user while setting up the test fixtures
        self.app.dependency_overrides[auth] = mock_auth(ADMIN, FEDTMULE)

        # Create org unit under the root unit
        self.org_unit_uuid_1 = self.assertRequest(
            self.url_create,
            json=self.create_org_unit_payload,
            status_code=HTTP_201_CREATED,
        )

        # Create empty org unit under the above unit
        self.create_org_unit_payload["parent"]["uuid"] = self.org_unit_uuid_1
        self.org_unit_uuid_2 = self.assertRequest(
            self.url_create,
            json=self.create_org_unit_payload,
            status_code=HTTP_201_CREATED,
        )

        # Set parent uuid back to original value (root uuid)
        self.create_org_unit_payload["parent"]["uuid"] = ROOT_UNIT

        # Set Anders And as the owner of the first of the newly created units
        self.create_owner_payload[0]["org_unit"]["uuid"] = self.org_unit_uuid_1
        self.assertRequest(
            self.url_create_detail,
            json=self.create_owner_payload,
            status_code=HTTP_201_CREATED,
        )

        # Set the user back to a normal user, i.e. Bruce Lee
        self.app.dependency_overrides[auth] = mock_auth()


@pytest.mark.usefixtures("load_fixture_data_with_reset")
class TestCreateOrgUnit(TestCommon):
    @parameterized.expand(
        [
            (None, None, HTTP_403_FORBIDDEN),
            (OWNER, ANDERS_AND, HTTP_403_FORBIDDEN),
            (ADMIN, ANDERS_AND, HTTP_201_CREATED),
        ]
    )
    @util.override_config(Settings(keycloak_rbac_enabled=True))
    def test_create_org_unit(self, role: str, userid: str, status_code: int):
        """
        Test of write access for the following cases:
        1) Normal user (no roles set)
        2) User with the owner role, but not owner of the relevant entity
        3) User with the admin role

        :param role: the role of the user
        :param userid: the UUID of the user
        :param status_code: the expected HTTP status code
        """
        self.app.dependency_overrides[auth] = mock_auth(role, userid)

        self.assertRequest(
            self.url_create, json=self.create_org_unit_payload, status_code=status_code
        )

    @util.override_config(Settings(keycloak_rbac_enabled=True))
    def test_201_when_creating_unit_as_owner_of_parent_unit(self):
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)
        self.create_org_unit_payload["parent"] = {"uuid": HUM_UNIT}

        self.assertRequest(
            self.url_create,
            json=self.create_org_unit_payload,
            status_code=HTTP_201_CREATED,
        )

    @parameterized.expand(
        [
            (None, None, HTTP_403_FORBIDDEN),
            (OWNER, ANDERS_AND, HTTP_403_FORBIDDEN),
            (ADMIN, ANDERS_AND, HTTP_201_CREATED),
        ]
    )
    @util.override_config(Settings(keycloak_rbac_enabled=True))
    def test_create_top_level_unit(self, role: str, userid: str, status_code: int):
        """
        Test of write access for the following cases:
        1) Normal user (no roles set)
        2) User with the owner role
        3) User with the admin role

        :param role: the role of the user
        :param userid: the UUID of the user
        :param status_code: the expected HTTP status code
        """
        self.app.dependency_overrides[auth] = mock_auth(role, userid)
        self.create_org_unit_payload.pop("parent")

        self.assertRequest(
            self.url_create, json=self.create_org_unit_payload, status_code=status_code
        )


@pytest.mark.usefixtures("load_fixture_data_with_reset")
class TestRenameOrgUnit(TestCommon):
    @parameterized.expand(
        [
            (None, None, HTTP_403_FORBIDDEN),
            (OWNER, FEDTMULE, HTTP_403_FORBIDDEN),
            (OWNER, ANDERS_AND, HTTP_200_OK),
            (ADMIN, FEDTMULE, HTTP_200_OK),
        ]
    )
    @util.override_config(Settings(keycloak_rbac_enabled=True))
    def test_rename_org_unit(self, role: str, userid: str, status_code: int):
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
            self.url_edit_detail, json=self.rename_payload, status_code=status_code
        )


@pytest.mark.usefixtures("load_fixture_data_with_reset")
class TestTerminateOrgUnit(TestCommon):
    def setUp(self):
        super().setUp()

        self.url_terminate = f"/service/ou/{self.org_unit_uuid_2}/terminate"

        # Payload for terminating the newly created org unit
        self.terminate_payload = {
            "validity": {"to": datetime.today().strftime("%Y-%m-%d")}
        }

    @parameterized.expand(
        [
            (None, None, HTTP_403_FORBIDDEN),
            (OWNER, FEDTMULE, HTTP_403_FORBIDDEN),
            (OWNER, ANDERS_AND, HTTP_200_OK),
            (ADMIN, FEDTMULE, HTTP_200_OK),
        ]
    )
    @util.override_config(Settings(keycloak_rbac_enabled=True))
    def test_terminate_org_unit(self, role: str, userid: str, status_code: int):
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
            self.url_terminate, json=self.terminate_payload, status_code=status_code
        )


@pytest.mark.usefixtures("load_fixture_data_with_reset")
class TestCreateDetail(TestCommon):
    def setUp(self):
        super().setUp()

        self.url_create_detail = "/service/details/create"

        # Payload for creating detail (email address) on org unit
        self.create_detail_payload = [
            {
                "type": "address",
                "org": {
                    "name": "Aarhus Universitet",
                    "user_key": "AU",
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                },
                "visibility": {
                    "uuid": "f63ad763-0e53-4972-a6a9-63b42a0f8cb7",
                    "name": "Må vises externt",
                    "user_key": "Ekstern",
                    "example": None,
                    "scope": "INTERNAL",
                    "owner": None,
                },
                "address_type": {
                    "uuid": "73360db1-bad3-4167-ac73-8d827c0c8751",
                    "name": "Email",
                    "user_key": "EmailUnit",
                    "example": None,
                    "scope": "EMAIL",
                    "owner": None,
                },
                "value": "bruce@kung.fu",
                "validity": {"from": "2020-06-22", "to": None},
                "org_unit": {"uuid": HUM_UNIT},
            }
        ]

    @parameterized.expand(
        [
            (None, None, HTTP_403_FORBIDDEN),
            (OWNER, FEDTMULE, HTTP_403_FORBIDDEN),
            (OWNER, ANDERS_AND, HTTP_201_CREATED),
            (ADMIN, FEDTMULE, HTTP_201_CREATED),
        ]
    )
    @util.override_config(Settings(keycloak_rbac_enabled=True))
    def test_create_detail(self, role: str, userid: str, status_code: int):
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
            self.url_create_detail,
            json=self.create_detail_payload,
            status_code=status_code,
        )

    @util.override_config(Settings(keycloak_rbac_enabled=True))
    def test_201_when_creating_multiple_details_as_owner_of_unit(self):
        # Use user "Anders And" (who owns the unit)
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

        self.create_detail_payload.append(self.create_detail_payload[0])

        self.assertRequest(
            self.url_create_detail,
            json=self.create_detail_payload,
            status_code=HTTP_201_CREATED,
        )

    @util.override_config(Settings(keycloak_rbac_enabled=True))
    def test_400_when_creating_multiple_details_with_different_types(self):
        # Use user "Anders And" (who owns the unit)
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

        self.create_detail_payload.append(deepcopy(self.create_detail_payload[0]))
        self.create_detail_payload[1]["type"] = "org_unit"

        self.assertRequest(
            self.url_create_detail,
            json=self.create_detail_payload,
            status_code=HTTP_400_BAD_REQUEST,
        )


@pytest.mark.usefixtures("load_fixture_data_with_reset")
class TestEditDetail(TestCommon):
    def setUp(self):
        super().setUp()

        # Payload for editing detail (phone number) on org unit (hum)
        self.edit_detail_payload = {
            "type": "address",
            "uuid": "55848eca-4e9e-4f30-954b-78d55eec0473",
            "data": {
                "uuid": "55848eca-4e9e-4f30-954b-78d55eec0473",
                "user_key": "8715 0000",
                "validity": {"from": "2021-07-29", "to": None},
                "address_type": {
                    "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                    "name": "Telefon",
                    "user_key": "OrgEnhedTelefon",
                    "example": "20304060",
                    "scope": "PHONE",
                    "owner": None,
                },
                "href": "tel:+4587150000",
                "name": "+4587150000",
                "value": "+4587150001",
                "value2": None,
                "visibility": {
                    "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                    "name": "Telefon",
                    "user_key": "OrgEnhedTelefon",
                    "example": "20304060",
                    "scope": "PHONE",
                    "owner": None,
                },
                "org_unit": {
                    "name": "Humanistisk fakultet",
                    "user_key": "hum",
                    "uuid": HUM_UNIT,
                    "validity": {"from": "2016-01-01", "to": None},
                },
                "type": "address",
                "org": {
                    "name": "Aarhus Universitet",
                    "user_key": "AU",
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                },
            },
            "org_unit": {"uuid": HUM_UNIT},
        }

    @parameterized.expand(
        [
            (None, None, HTTP_403_FORBIDDEN),
            (OWNER, FEDTMULE, HTTP_403_FORBIDDEN),
            (OWNER, ANDERS_AND, HTTP_200_OK),
            (ADMIN, FEDTMULE, HTTP_200_OK),
        ]
    )
    @util.override_config(Settings(keycloak_rbac_enabled=True))
    def test_edit_detail(self, role: str, userid: str, status_code: int):
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
            self.url_edit_detail, json=self.edit_detail_payload, status_code=status_code
        )


@pytest.mark.usefixtures("load_fixture_data_with_reset")
class TestIndirectOwnership(TestCommon):
    """
    Test that an org unit can be modified by a user who owns the parent
    unit but not the unit subject to modification itself.
    """

    @parameterized.expand(
        [
            (OWNER, ANDERS_AND, HTTP_200_OK),
            (OWNER, FEDTMULE, HTTP_403_FORBIDDEN),
        ]
    )
    @util.override_config(Settings(keycloak_rbac_enabled=True))
    def test_rename_subunit(self, role: str, userid: str, status_code: int):
        self.app.dependency_overrides[auth] = mock_auth(role, userid)
        self.rename_payload["data"]["uuid"] = self.org_unit_uuid_2

        self.assertRequest(
            self.url_edit_detail, json=self.rename_payload, status_code=status_code
        )


@pytest.mark.usefixtures("load_fixture_data_with_reset")
class TestMoveOrgUnit(TestCommon):
    def setUp(self):
        super().setUp()

        self.move_unit_payload = {
            "type": "org_unit",
            "data": {
                "parent": {"uuid": "bdfda9c8-08e8-46aa-8586-c9c54563e1f4"},
                "uuid": HUM_UNIT,
                "clamp": True,
                "validity": {"from": "2021-07-30"},
            },
        }

    @util.override_config(Settings(keycloak_rbac_enabled=True))
    def test_owner_of_unit_moves_unit_to_subunit_of_owned_unit(self):
        # Use user "Anders And" (who owns the parent unit)
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)
        self.move_unit_payload["data"]["parent"]["uuid"] = self.org_unit_uuid_2

        self.assertRequest(
            self.url_edit_detail, json=self.move_unit_payload, status_code=HTTP_200_OK
        )

    @util.override_config(Settings(keycloak_rbac_enabled=True))
    def test_owner_of_unit_moves_unit_to_owned_unit(self):
        # Use user "Anders And" (who owns the parent unit)
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)
        self.move_unit_payload["data"]["parent"]["uuid"] = self.org_unit_uuid_1

        self.assertRequest(
            self.url_edit_detail, json=self.move_unit_payload, status_code=HTTP_200_OK
        )

    @util.override_config(Settings(keycloak_rbac_enabled=True))
    def test_non_owner_of_unit_moves_unit_to_subunit_of_non_owned_unit(self):
        self.app.dependency_overrides[auth] = mock_auth(OWNER, FEDTMULE)
        self.move_unit_payload["data"]["parent"]["uuid"] = self.org_unit_uuid_2

        self.assertRequest(
            self.url_edit_detail,
            json=self.move_unit_payload,
            status_code=HTTP_403_FORBIDDEN,
        )

    @util.override_config(Settings(keycloak_rbac_enabled=True))
    def test_owner_of_unit_moves_unit_to_subunit_of_non_owned_unit(self):
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)
        self.move_unit_payload["data"]["parent"]["uuid"] = ROOT_UNIT

        self.assertRequest(
            self.url_edit_detail,
            json=self.move_unit_payload,
            status_code=HTTP_403_FORBIDDEN,
        )

    @util.override_config(Settings(keycloak_rbac_enabled=True))
    def test_non_owner_of_unit_moves_unit_to_non_owned_unit(self):
        self.app.dependency_overrides[auth] = mock_auth(OWNER, FEDTMULE)
        self.move_unit_payload["data"]["parent"]["uuid"] = self.org_unit_uuid_1

        self.assertRequest(
            self.url_edit_detail,
            json=self.move_unit_payload,
            status_code=HTTP_403_FORBIDDEN,
        )

    @util.override_config(Settings(keycloak_rbac_enabled=True))
    def test_owner_moves_owned_subunit_to_owned_subunit(self):
        # Use user "Anders And" (who owns the parent unit)
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

        self.move_unit_payload["data"]["uuid"] = FILOSOFISK_INSTITUT
        self.move_unit_payload["data"]["parent"]["uuid"] = self.org_unit_uuid_2

        self.assertRequest(
            self.url_edit_detail, json=self.move_unit_payload, status_code=HTTP_200_OK
        )


@pytest.mark.usefixtures("load_fixture_data_with_reset")
class TestTerminateOrgUnitDetail(TestCommon):
    @util.override_config(Settings(keycloak_rbac_enabled=True))
    def test_terminate_address_as_owner_of_unit(self):
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

        payload = {
            "type": "address",
            "uuid": "55848eca-4e9e-4f30-954b-78d55eec0473",
            "validity": {"to": "2021-07-16"},
        }

        self.assertRequest(
            self.url_terminate_detail, json=payload, status_code=HTTP_200_OK
        )

    @util.override_config(Settings(keycloak_rbac_enabled=True))
    def test_terminate_association_as_owner_of_unit(self):
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

        payload = {
            "type": "association",
            "uuid": "c2153d5d-4a2b-492d-a18c-c498f7bb6221",
            "validity": {"to": "2021-07-16"},
        }

        self.assertRequest(
            self.url_terminate_detail, json=payload, status_code=HTTP_200_OK
        )

    @util.override_config(Settings(keycloak_rbac_enabled=True))
    def test_terminate_manager_as_owner_of_unit(self):
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

        payload = {
            "type": "manager",
            "uuid": "05609702-977f-4869-9fb4-50ad74c6999a",
            "validity": {"to": "2021-07-16"},
        }

        self.assertRequest(
            self.url_terminate_detail, json=payload, status_code=HTTP_200_OK
        )

    @util.override_config(Settings(keycloak_rbac_enabled=True))
    def test_terminate_org_unit_as_owner_of_unit(self):
        self.app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

        payload = {
            "type": "org_unit",
            "uuid": HUM_UNIT,
            "validity": {"to": "2021-07-16"},
        }

        self.assertRequest(
            self.url_terminate_detail, json=payload, status_code=HTTP_200_OK
        )
