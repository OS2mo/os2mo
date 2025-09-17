# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import copy
import unittest.mock
from uuid import UUID
from uuid import uuid4

import pytest
from mora.auth.exceptions import AuthorizationError
from mora.auth.keycloak.models import Token
from mora.auth.keycloak.owner import _get_entity_owners
from mora.auth.keycloak.owner import get_ancestor_owners
from mora.auth.keycloak.rbac import _get_employee_uuid
from mora.auth.keycloak.rbac import _get_employee_uuid_via_token
from mora.auth.keycloak.rbac import _rbac
from mora.config import Settings
from mora.mapping import ADMIN
from mora.mapping import OWNER
from mora.mapping import EntityType

from tests.test_integration_rbac import ANDERS_AND
from tests.test_integration_rbac import FEDTMULE
from tests.test_integration_rbac import mock_auth

ORG_UNIT_1 = "10000000-0000-0000-0000-000000000000"
ORG_UNIT_2 = "20000000-0000-0000-0000-000000000000"
FILOSOFISK_INSTITUT = "85715fc7-925d-401b-822d-467eb4b163b6"


class TestRole:
    async def test_raise_exception_for_normal_user(self):
        # The user is neither admin or owner
        token = mock_auth()()
        with pytest.raises(AuthorizationError):
            await _rbac(token, None, False)

    async def test_raise_exception_when_role_is_owner_and_admin_only_true(self):
        token = mock_auth(OWNER, ANDERS_AND)()
        with pytest.raises(AuthorizationError):
            await _rbac(token, None, True)

    async def test_return_when_role_is_admin(self):
        token = mock_auth(ADMIN, ANDERS_AND)()
        r = await _rbac(token, None, False)
        assert r is None


class TestOwner:
    async def test_raise_exception_when_owner_but_no_user_uuid(self):
        token = mock_auth(role=OWNER, user_uuid=None)()  # noqa: FURB120
        with pytest.raises(AuthorizationError):
            await _rbac(token, None, False)


class TestOwnerSingleOrgUnit:
    """
    This class covers test cases where the user has the owner role and
    the users modifications involves a single org unit (i.e. we are not
    moving an org unit in any of these tests).
    """

    @unittest.mock.patch("mora.auth.keycloak.rbac.get_owners")
    @unittest.mock.patch("mora.auth.keycloak.rbac.uuid_extractor.get_entity_type")
    @unittest.mock.patch("mora.auth.keycloak.rbac.uuid_extractor.get_entity_uuids")
    async def test_return_when_owner_owns_unit_or_ancestor(
        self, mock_uuids, mock_get_entity_type, mock_get_owners
    ):
        token = mock_auth(OWNER, ANDERS_AND)()
        mock_uuids.return_value = {ORG_UNIT_1}
        mock_get_entity_type.return_value = EntityType.ORG_UNIT
        mock_get_owners.return_value = {UUID(ANDERS_AND), UUID(FEDTMULE)}

        r = await _rbac(token, None, False)
        assert r is None

    @unittest.mock.patch("mora.auth.keycloak.rbac.get_owners")
    @unittest.mock.patch("mora.auth.keycloak.rbac.uuid_extractor.get_entity_type")
    @unittest.mock.patch("mora.auth.keycloak.rbac.uuid_extractor.get_entity_uuids")
    async def test_raise_exception_when_owner_does_not_owns_unit_or_ancestor(
        self, mock_uuids, mock_get_entity_type, mock_get_owners
    ):
        token = mock_auth(OWNER, ANDERS_AND)()
        mock_uuids.return_value = {ORG_UNIT_1}
        mock_get_entity_type.return_value = EntityType.ORG_UNIT
        mock_get_owners.return_value = {UUID(FEDTMULE)}

        with pytest.raises(AuthorizationError):
            await _rbac(token, None, False)

    @unittest.mock.patch("mora.auth.keycloak.rbac.get_owners")
    @unittest.mock.patch("mora.auth.keycloak.rbac.uuid_extractor.get_entity_type")
    @unittest.mock.patch("mora.auth.keycloak.rbac.uuid_extractor.get_entity_uuids")
    async def test_raise_exception_when_no_owners_in_ancestors(
        self, mock_uuids, mock_get_entity_type, mock_get_owners
    ):
        token = mock_auth(OWNER, ANDERS_AND)()
        mock_uuids.return_value = {ORG_UNIT_1}
        mock_get_entity_type.return_value = EntityType.ORG_UNIT
        mock_get_owners.return_value = set()

        with pytest.raises(AuthorizationError):
            await _rbac(token, None, False)

    @unittest.mock.patch("mora.auth.keycloak.rbac.get_owners")
    @unittest.mock.patch("mora.auth.keycloak.rbac.uuid_extractor.get_entity_type")
    @unittest.mock.patch("mora.auth.keycloak.rbac.uuid_extractor.get_entity_uuids")
    async def test_raise_exception_when_uuids_list_empty(
        self, mock_uuids, mock_get_entity_type, mock_get_owners
    ):
        # This happens when creating a top-level org unit
        token = mock_auth(OWNER, ANDERS_AND)()
        mock_uuids.return_value = set()
        mock_get_entity_type.return_value = EntityType.ORG_UNIT
        mock_get_owners.return_value = None

        with pytest.raises(AuthorizationError):
            await _rbac(token, None, False)


class TestOwnerMultipleOrgUnits:
    """
    This class covers test cases where the user has the owner role and
    the users modifications involves two org units (i.e. when we are
    moving an org unit).
    """

    @unittest.mock.patch("mora.auth.keycloak.rbac.get_owners")
    @unittest.mock.patch("mora.auth.keycloak.rbac.uuid_extractor.get_entity_type")
    @unittest.mock.patch("mora.auth.keycloak.rbac.uuid_extractor.get_entity_uuids")
    async def test_raise_exception_when_owner_not_in_source_or_target_units(
        self, mock_uuids, mock_get_entity_type, mock_get_owners
    ):
        token = mock_auth(OWNER, ANDERS_AND)()
        mock_uuids.return_value = {ORG_UNIT_1, ORG_UNIT_2}
        mock_get_entity_type.return_value = EntityType.ORG_UNIT
        mock_get_owners.return_value = set()

        with pytest.raises(AuthorizationError):
            await _rbac(token, None, False)

    @unittest.mock.patch("mora.auth.keycloak.rbac.get_owners")
    @unittest.mock.patch("mora.auth.keycloak.rbac.uuid_extractor.get_entity_type")
    @unittest.mock.patch("mora.auth.keycloak.rbac.uuid_extractor.get_entity_uuids")
    async def test_raise_exception_when_owner_not_in_target_unit(
        self, mock_uuids, mock_get_entity_type, mock_get_owners
    ):
        token = mock_auth(OWNER, ANDERS_AND)()
        mock_uuids.return_value = {ORG_UNIT_1, ORG_UNIT_2}
        mock_get_entity_type.return_value = EntityType.ORG_UNIT
        mock_get_owners.side_effect = [{ANDERS_AND}, set()]

        with pytest.raises(AuthorizationError):
            await _rbac(token, None, False)

    @unittest.mock.patch("mora.auth.keycloak.rbac.get_owners")
    @unittest.mock.patch("mora.auth.keycloak.rbac.uuid_extractor.get_entity_type")
    @unittest.mock.patch("mora.auth.keycloak.rbac.uuid_extractor.get_entity_uuids")
    async def test_raise_exception_when_owner_not_in_source_unit(
        self, mock_uuids, mock_get_entity_type, mock_get_owners
    ):
        token = mock_auth(OWNER, ANDERS_AND)()
        mock_uuids.return_value = {ORG_UNIT_1, ORG_UNIT_2}
        mock_get_entity_type.return_value = EntityType.ORG_UNIT
        mock_get_owners.side_effect = [set(), {ANDERS_AND}]

        with pytest.raises(AuthorizationError):
            await _rbac(token, None, False)

    @unittest.mock.patch("mora.auth.keycloak.rbac.get_owners")
    @unittest.mock.patch("mora.auth.keycloak.rbac.uuid_extractor.get_entity_type")
    @unittest.mock.patch("mora.auth.keycloak.rbac.uuid_extractor.get_entity_uuids")
    async def test_return_when_owner_in_source_and_target_units(
        self, mock_uuids, mock_get_entity_type, mock_get_owners
    ):
        token = mock_auth(OWNER, ANDERS_AND)()
        mock_uuids.return_value = {ORG_UNIT_1, ORG_UNIT_2}
        mock_get_entity_type.return_value = EntityType.ORG_UNIT
        mock_get_owners.return_value = {UUID(ANDERS_AND)}

        r = await _rbac(token, None, False)
        assert r is None


class TestGetAncestorOwners:
    def set_up(self) -> None:
        self.org_unit_tree = [
            {
                "name": "Overordnet Enhed",
                "user_key": "root",
                "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                "validity": {"from": "2016-01-01", "to": None},
                "children": [
                    {
                        "name": "Humanistisk fakultet",
                        "user_key": "hum",
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "validity": {"from": "2016-01-01", "to": None},
                        "children": [
                            {
                                "name": "Filosofisk Institut",
                                "user_key": "fil",
                                "uuid": "85715fc7-925d-401b-822d-467eb4b163b6",
                                "validity": {"from": "2016-01-01", "to": None},
                            }
                        ],
                    }
                ],
            }
        ]

        self.owners = [
            {
                "uuid": "c16ff527-3501-42f7-a942-e606c6c1a0a7",
                "user_key": "f2b92485-2564-41c4-8f0d-3e09190253aa",
                "validity": {"from": "2021-06-18", "to": None},
                "owner_inference_priority": None,
                "owner": {
                    "givenname": "Anders",
                    "surname": "And",
                    "name": "Anders And",
                    "nickname_givenname": "Donald",
                    "nickname_surname": "Duck",
                    "nickname": "Donald Duck",
                    "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                    "seniority": None,
                },
                "org_unit": {
                    "name": "Humanistisk fakultet",
                    "user_key": "hum",
                    "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                    "validity": {"from": "2016-01-01", "to": None},
                },
                "person": None,
            }
        ]

    @unittest.mock.patch("mora.auth.keycloak.owner.common.get_connector")
    @unittest.mock.patch("mora.auth.keycloak.owner.OwnerReader.get_from_type")
    @unittest.mock.patch("mora.auth.keycloak.owner.mora.service.orgunit.get_unit_tree")
    async def test_anders_and_in_owners(
        self, mock_get_unit_tree, mock_get_from_type, mock_get_connector
    ):
        self.set_up()
        mock_get_unit_tree.return_value = self.org_unit_tree
        mock_get_from_type.side_effect = [[], self.owners, []]
        mock_get_connector.return_value = None

        ancestor_owners = await get_ancestor_owners(UUID(FILOSOFISK_INSTITUT))

        assert {UUID(ANDERS_AND)} == ancestor_owners

    @unittest.mock.patch("mora.auth.keycloak.owner.common.get_connector")
    @unittest.mock.patch("mora.auth.keycloak.owner.OwnerReader.get_from_type")
    @unittest.mock.patch("mora.auth.keycloak.owner.mora.service.orgunit.get_unit_tree")
    async def test_fedtmule_in_owners(
        self, mock_get_unit_tree, mock_get_from_type, mock_get_connector
    ):
        self.set_up()
        mock_get_unit_tree.return_value = self.org_unit_tree
        self.owners[0]["owner"]["uuid"] = FEDTMULE
        mock_get_from_type.side_effect = [[], self.owners, []]
        mock_get_connector.return_value = None

        ancestor_owners = await get_ancestor_owners(UUID(FILOSOFISK_INSTITUT))

        assert {UUID(FEDTMULE)} == ancestor_owners

    @unittest.mock.patch("mora.auth.keycloak.owner.common.get_connector")
    @unittest.mock.patch("mora.auth.keycloak.owner.OwnerReader.get_from_type")
    @unittest.mock.patch("mora.auth.keycloak.owner.mora.service.orgunit.get_unit_tree")
    async def test_anders_and_and_fedtmule_in_owners(
        self, mock_get_unit_tree, mock_get_from_type, mock_get_connector
    ):
        self.set_up()
        mock_get_unit_tree.return_value = self.org_unit_tree

        anders_and = self.owners[0]
        fedtmule = copy.deepcopy(anders_and)
        fedtmule["owner"]["uuid"] = FEDTMULE
        self.owners.append(fedtmule)

        mock_get_from_type.side_effect = [[], self.owners, []]
        mock_get_connector.return_value = None

        ancestor_owners = await get_ancestor_owners(UUID(FILOSOFISK_INSTITUT))

        assert {UUID(ANDERS_AND), UUID(FEDTMULE)} == ancestor_owners

    @unittest.mock.patch("mora.auth.keycloak.owner.common.get_connector")
    @unittest.mock.patch("mora.auth.keycloak.owner.OwnerReader.get_from_type")
    @unittest.mock.patch("mora.auth.keycloak.owner.mora.service.orgunit.get_unit_tree")
    async def test_no_owners(
        self, mock_get_unit_tree, mock_get_from_type, mock_get_connector
    ):
        self.set_up()
        mock_get_unit_tree.return_value = self.org_unit_tree
        mock_get_from_type.return_value = []
        mock_get_connector.return_value = None

        ancestor_owners = await get_ancestor_owners(UUID(FILOSOFISK_INSTITUT))

        assert set() == ancestor_owners


class TestGetEntityOwners:
    @unittest.mock.patch("mora.auth.keycloak.owner.common.get_connector")
    @unittest.mock.patch("mora.auth.keycloak.owner.OwnerReader.get_from_type")
    async def test_filter_empty_dicts_and_vacant_owners(
        self, mock_get_from_type, mock_get_connector
    ):
        # Arrange
        owner_uuid = uuid4()
        mock_get_from_type.return_value = [
            {},
            {"owner": None},  # Happens for vacant owners
            {"owner": {"uuid": str(owner_uuid)}},
        ]

        # Act
        owners = await _get_entity_owners(uuid4(), EntityType.ORG_UNIT)

        # Assert
        assert owners == {owner_uuid}


def test__get_employee_uuid_via_token() -> None:
    uuid = uuid4()
    employee_uuid = _get_employee_uuid_via_token(
        Token(
            azp="azp",
            email="test@example.org",
            preferred_username="Test",
            uuid=uuid,
        )
    )
    assert employee_uuid == uuid


async def test__get_employee_uuid_via_token_strategy():
    uuid = uuid4()
    token = Token(
        azp="azp",
        email="test@example.org",
        preferred_username="Test",
        uuid=uuid,
    )
    assert await _get_employee_uuid(token) == uuid


@unittest.mock.patch("mora.auth.keycloak.rbac.mora.config.get_settings")
@unittest.mock.patch("mora.auth.keycloak.rbac._get_employee_uuid_via_it_system")
async def test__get_employee_uuid_via_it_system_strategy(mock, mock_get_settings):
    it_system_uuid = uuid4()
    uuid = uuid4()

    mock_get_settings.return_value = Settings(
        keycloak_rbac_authoritative_it_system_for_owners=it_system_uuid
    )

    token = Token(
        azp="azp",
        email="test@example.org",
        preferred_username="Test",
        uuid=uuid,
    )

    await _get_employee_uuid(token)

    # We are only testing that the correct strategy is selected
    mock.assert_awaited_once_with(it_system_uuid, uuid)
