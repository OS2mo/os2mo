#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import tempfile

import freezegun
import pytest

from .. import util
from mora import util as mora_util
from mora.config import Settings
from mora.integrations import serviceplatformen

# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------

pytestmark = pytest.mark.asyncio


@freezegun.freeze_time("2017-01-01", tz_offset=1)
class TestCPR:
    """Test CPR lookup capabilities.

    Time is frozen to too_early/too_late keeps working as expected.
    This functionality is in dummy mode per default when testing.
    """

    async def test_cpr_lookup_dummy_mode_true(self, async_service_client):
        async with async_service_client as client:
            response = await client.get("/service/e/cpr_lookup/?q=0101501234")
        assert response.json() == {"name": "Merle Mortensen", "cpr_no": "0101501234"}

    async def test_cpr_lookup_dummy_mode_true_too_early(self, async_service_client):
        assert mora_util.get_cpr_birthdate(2004936541).year == 1893
        async with async_service_client as client:
            response = await client.get("/service/e/cpr_lookup/?q=2004936541")
        assert response.status_code == 404
        assert response.json() == {
            "cpr": "2004936541",
            "description": "No person found for given CPR number.",
            "error": True,
            "error_key": "V_NO_PERSON_FOR_CPR",
            "status": 404,
        }

    async def test_cpr_lookup_dummy_mode_true_too_late(self, async_service_client):
        assert mora_util.get_cpr_birthdate(2004256543).year == 2025
        async with async_service_client as client:
            response = await client.get("/service/e/cpr_lookup/?q=2004256543")
        assert response.status_code == 404
        assert response.json() == {
            "cpr": "2004256543",
            "description": "No person found for given CPR number.",
            "error": True,
            "error_key": "V_NO_PERSON_FOR_CPR",
            "status": 404,
        }

    async def test_cpr_lookup_dummy_mode_true_not_cpr_number(
        self, async_service_client
    ):
        # This test originally used 1337, however, that fails due to length as
        # the next test shows. 0000000000 is the correct length, but not a valid CPR.
        async with async_service_client as client:
            response = await client.get("/service/e/cpr_lookup/?q=0000000000")
        assert response.status_code == 400
        assert response.json() == {
            "cpr": "0000000000",
            "error_key": "V_CPR_NOT_VALID",
            "description": "Not a valid CPR number.",
            "error": True,
            "status": 400,
        }

    @pytest.mark.parametrize(
        "cpr", ["1234", "111111111", "1234567890123", "2222222222"]
    )
    async def test_cpr_lookup_raises_on_wrong_length(self, async_service_client, cpr):
        async with async_service_client as client:
            response = await client.get(f"/service/e/cpr_lookup/?q={cpr}")
        assert response.status_code == 400
        assert response.json() == {
            "cpr": cpr,
            "error_key": "V_CPR_NOT_VALID",
            "description": "Not a valid CPR number.",
            "error": True,
            "status": 400,
        }

    async def test_birthdate_validation_disabled(self, async_service_client):
        with util.override_config(Settings(cpr_validate_birthdate=False)):
            async with async_service_client as client:
                response = await client.get("/service/e/cpr_lookup/?q=0121501234")
        assert response.status_code == 200
        assert response.json() == {"name": "Naja Hansen", "cpr_no": "0121501234"}


class TestServiceplatformConfig:
    """Test configuration of Serviceplatformen integration."""

    def _sp_config(self, **overrides):
        UUID_OK = "12345678-9abc-def1-1111-111111111111"

        return {
            "sp_service_uuid": UUID_OK,
            "sp_agreement_uuid": UUID_OK,
            "sp_municipality_uuid": UUID_OK,
            "sp_system_uuid": UUID_OK,
            **overrides,
        }

    def test_serviceplatformen_dummy_true(self):
        """Bad/missing values in config are not considered in dummy mode."""
        with util.override_config(Settings(environment="production", dummy_mode=True)):
            assert serviceplatformen.check_config()

    def test_serviceplatformen_missing_path(self):
        override = Settings(
            environment="production", dummy_mode=False, **self._sp_config()
        )
        with util.override_config(override):
            with pytest.raises(ValueError, match="certificate path must be configured"):
                serviceplatformen.check_config()

    def test_serviceplatformen_empty_file(self):
        with tempfile.NamedTemporaryFile() as tf:
            override = Settings(
                environment="production",
                dummy_mode=False,
                **self._sp_config(sp_certificate_path=tf.name),
            )
            with util.override_config(override):
                with pytest.raises(ValueError, match="certificate can not be empty"):
                    serviceplatformen.check_config()
