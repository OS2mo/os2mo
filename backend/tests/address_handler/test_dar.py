# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from mora import exceptions
from mora.service.address_handler.dar import DARAddressHandler

from .. import util
from ..util import dar_loader

VALID_VALUE = "0a3f50a0-23c9-32b8-e044-0003ba298018"


async def test_from_effect():
    # Arrange
    effect = {"relationer": {"adresser": [{"urn": f"urn:dar:{VALID_VALUE}"}]}}
    with util.darmock("dawa-addresses.json", real_http=True):
        with dar_loader():
            address_handler = await DARAddressHandler.from_effect(effect)

        # Act
        actual_value = address_handler.value

        # Assert
        assert VALID_VALUE == actual_value


async def test_from_request():
    # Arrange
    request = {"value": VALID_VALUE}
    with util.darmock("dawa-addresses.json", real_http=True):
        with dar_loader():
            address_handler = await DARAddressHandler.from_request(request)

        # Act
        actual_value = address_handler.value

        # Assert
        assert VALID_VALUE == actual_value


async def test_get_mo_address():
    # Arrange
    request = {"value": VALID_VALUE}
    with util.darmock("dawa-addresses.json", real_http=True):
        with dar_loader():
            address_handler = await DARAddressHandler.from_request(request)

        expected = {
            "href": None,
            "name": "0a3f50a0-23c9-32b8-e044-0003ba298018",
            "value": "0a3f50a0-23c9-32b8-e044-0003ba298018",
            "value2": None,
        }

        # Act
        actual = await address_handler.get_mo_address_and_properties()

        # Assert
        assert expected == actual


async def test_validation_fails_on_invalid_value():
    # Arrange
    value = "1234"  # Not a valid DAR UUID

    # Act & Assert
    with util.darmock("dawa-addresses.json", real_http=True):
        with pytest.raises(exceptions.HTTPException):
            with dar_loader():
                await DARAddressHandler.validate_value(value)


async def test_validation_fails_on_unknown_uuid():
    # Arrange
    value = "e30645d3-2c2b-4b9f-9b7a-3b7fc0b4b80d"  # Not a valid DAR UUID

    # Act & Assert
    with util.darmock("dawa-addresses.json", real_http=True):
        with pytest.raises(exceptions.HTTPException):
            with dar_loader():
                await DARAddressHandler.validate_value(value)


async def test_validation_succeeds_on_correct_uuid():
    # Act & Assert
    # Assert that no exception is raised
    with util.darmock("dawa-addresses.json", real_http=True):
        with dar_loader():
            await DARAddressHandler.validate_value(VALID_VALUE)


async def test_validation_succeeds_with_force():
    # Arrange
    value = "GARBAGEGARBAGE"  # Not a valid DAR UUID

    # Act & Assert
    with util.darmock("dawa-addresses.json", real_http=True):
        async with util.patch_query_args({"force": "1"}):
            await DARAddressHandler.validate_value(value)


async def test_failed_lookup_from_request():
    """Ensure that invalid DAR UUIDs fail validation on request"""
    # Arrange
    # Nonexisting DAR UUID should fail
    value = "300f16fd-fb60-4fec-8a2a-8d391e86bf3f"

    # Act & Assert
    with util.darmock("dawa-addresses.json", real_http=True):
        with pytest.raises(exceptions.HTTPException) as err:
            request = {"value": value}
            with dar_loader():
                await DARAddressHandler.from_request(request)

        assert {
            "description": "Invalid address",
            "error": True,
            "error_key": "V_INVALID_ADDRESS_DAR",
            "status": 400,
            "value": "300f16fd-fb60-4fec-8a2a-8d391e86bf3f",
        } == err.value.detail


async def test_lookup_from_request_with_force_succeeds():
    """Ensure that validation is skipped when force is True"""
    # Arrange
    # Nonexisting DAR UUID
    value = "00000000-0000-0000-0000-000000000000"

    expected = {
        "href": None,
        "name": "00000000-0000-0000-0000-000000000000",
        "value": "00000000-0000-0000-0000-000000000000",
        "value2": None,
    }

    # Act & Assert
    with util.darmock("dawa-addresses.json", real_http=True):
        async with util.patch_query_args({"force": "1"}):
            request = {"value": value}
            handler = await DARAddressHandler.from_request(request)
            actual = await handler.get_mo_address_and_properties()
            assert expected == actual


async def test_failed_lookup_from_effect():
    """Ensure that failed effect lookups are handled appropriately"""
    # Arrange
    # Nonexisting DAR UUID should fail
    value = "300f16fd-fb60-4fec-8a2a-8d391e86bf3f"

    expected = {
        "href": None,
        "name": "Ukendt",
        "value": "300f16fd-fb60-4fec-8a2a-8d391e86bf3f",
        "value2": None,
    }

    # Act
    effect = {"relationer": {"adresser": [{"urn": f"urn:dar:{value}"}]}}
    with util.darmock("dawa-addresses.json", real_http=True):
        with dar_loader():
            address_handler = await DARAddressHandler.from_effect(effect)

        assert expected == await address_handler.get_mo_address_and_properties()


def test_get_lora_address():
    # Arrange
    visibility = "d99b500c-34b4-4771-9381-5c989eede969"
    address_handler = DARAddressHandler(VALID_VALUE, visibility)

    expected = {"objekttype": "DAR", "urn": f"urn:dar:{VALID_VALUE}"}

    # Act
    actual = address_handler.get_lora_address()

    # Assert
    assert expected == actual
