# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest import mock

import pytest

from mora.service.handlers import RequestHandler
from mora.service.handlers import RequestType


class _DummyRequestHandler(RequestHandler):
    # We cannot instantiate `RequestHandler` directly in our tests, as it is an abstract
    # base class. Instead, we implement this dummy subclass and test that.

    role_type = "dummy"

    async def prepare_create(self, request: dict):
        pass

    async def prepare_edit(self, request: dict):
        pass

    async def prepare_refresh(self, request: dict):
        pass

    async def prepare_terminate(self, request: dict):
        pass


class TestHandlerValidateDetailRequestsAsGroups:
    @pytest.mark.asyncio
    async def test_one_call_per_group_validation(self):
        """Test that multiple MO objects trigger only one call to the relevant
        implementation of `GroupValidation.validate`.
        """

        # Construct request with two non-consecutive "IT User" MO objects, and one
        # "Association" MO object.
        #
        # "IT User" MO objects are validated since
        # `ItsystemRequestHandler.group_validations` contains `ITUserGroupValidation`.
        #
        # "Association" MO objects are not validated since
        # `AssociationRequestHandler.group_validations` is empty.

        request = {
            "details": [
                {"type": "it"},
                {"type": "association"},
                {"type": "it"},
            ]
        }

        # Assert that the expected validation method is called exactly once
        instance = _DummyRequestHandler(request, RequestType.CREATE)
        with mock.patch(
            "mora.service.itsystem.ITUserUniqueGroupValidation.validate"
        ) as mock_validate:
            await instance.validate_detail_requests_as_groups(request["details"])
            mock_validate.assert_called_once_with()
