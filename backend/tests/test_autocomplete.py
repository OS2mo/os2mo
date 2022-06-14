# SPDX-FileCopyrightText: 2022 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import pytest

from .cases import AsyncLoRATestCase
from .util import override_config
from mora.config import Settings
from mora.lora import AutocompleteScope
from mora.lora import Connector


@pytest.mark.asyncio
class TestAutocompleteScope(AsyncLoRATestCase):
    @override_config(Settings(confdb_autocomplete_use_new_api=True))
    async def test_regression(self):
        """Regression test: `AutocompleteScope.fetch` calls `_check_response` with an
        `aiohttp` response object, but `_check_response` has been updated to expect an
        `httpx` object instead. As a consequence, the response object does not have the
        `status_code` attribute expected by `_check_response` (it has a `status` attr
        instead.)
        See: #50878
        """
        connector = Connector()
        scope = AutocompleteScope(connector, "organisationsenhed")
        with pytest.raises(AttributeError):
            # Currently raises:
            # `AttributeError: 'ClientResponse' object has no attribute 'status_code'`
            await scope.fetch("phrase")
