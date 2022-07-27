# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest import mock
from uuid import uuid4

from parameterized import parameterized

from mora import mapping
from mora.service.facet import get_mo_object_primary_value
from mora.service.facet import is_class_primary
from mora.service.facet import is_class_uuid_primary


class TestPrimaryClassHelpers:
    """Tests the helper methods for determining the value of a `primary` MO class that
    reside in `mora.service.facet`.
    """

    @parameterized.expand(
        [
            # 1. MO class is primary
            ({mapping.USER_KEY: mapping.PRIMARY}, True),
            # 2. MO class is not primary
            ({mapping.USER_KEY: "non-primary"}, False),
            # 3. MO class is empty
            ({}, False),
        ]
    )
    def test_is_class_primary(self, mo_class: dict, expected_result: bool):
        assert is_class_primary(mo_class) == expected_result

    @parameterized.expand(
        [
            # MO class is primary
            (mapping.PRIMARY, True),
            # MO class is not primary
            ("not-primary", False),
        ]
    )
    async def test_is_class_uuid_primary(
        self, primary_class_user_key: str, expected_result: bool
    ):
        with self._mock_get_one_class(primary_class_user_key):
            actual_result = await is_class_uuid_primary("primary-class-uuid")
            assert actual_result == expected_result

    @parameterized.expand(
        [
            # 1. MO object contains a `primary` dict with a `user_key` "primary"
            ({mapping.PRIMARY: {mapping.USER_KEY: mapping.PRIMARY}}, True),
            # 2. MO object contains a `primary` dict with a `user_key` "non-primary"
            ({mapping.PRIMARY: {mapping.USER_KEY: "non-primary"}}, False),
            # 3. MO object contains a `primary` dict with a class UUID
            ({mapping.PRIMARY: {mapping.UUID: str(uuid4())}}, False),
            # 4. MO object contains a `primary` dict with an invalid class UUID
            ({mapping.PRIMARY: {mapping.UUID: "invalid"}}, False),
            # 5. MO object contains an empty `primary` dict
            ({mapping.PRIMARY: {}}, False),
            # 6. MO object contains a `primary` object which is None
            ({mapping.PRIMARY: None}, False),
        ]
    )
    async def test_get_mo_object_primary_value(
        self, mo_object: dict, expected_result: bool
    ):
        # Mock `get_one_class`, the return value is not important in this case
        with self._mock_get_one_class(""):
            assert (await get_mo_object_primary_value(mo_object)) == expected_result

    def _mock_get_one_class(self, primary_class_user_key: str):
        mock_get = mock.AsyncMock(
            return_value={mapping.USER_KEY: primary_class_user_key}
        )
        return mock.patch("mora.service.facet.get_one_class", mock_get)
