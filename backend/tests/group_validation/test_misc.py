# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest import mock

import pytest
from parameterized import parameterized

from mora import mapping
from mora.service.facet import is_class_uuid_primary


class TestPrimaryClassHelpers:
    @parameterized.expand(
        [
            (mapping.PRIMARY, True),
            ("not-primary", False),
        ]
    )
    @pytest.mark.asyncio
    async def test_is_class_uuid_primary(
        self, primary_class_user_key: str, expected_result: bool
    ):
        mock_get = mock.AsyncMock(
            return_value={mapping.USER_KEY: primary_class_user_key}
        )
        with mock.patch("mora.service.facet.get_one_class", mock_get):
            actual_result = await is_class_uuid_primary("primary-class-uuid")
            assert actual_result == expected_result
