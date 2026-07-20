# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import datetime
from pathlib import Path

import httpx
import pytest
import respx
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from fastapi.testclient import TestClient

from mora import mapping
from mora.config import Settings
from mora.service.shimmed import cpr as cpr_shim
from mora.service.shimmed import serviceplatformen

SP_UUID = "12345678-9abc-def1-1111-111111111111"


@pytest.mark.parametrize(
    "cpr_number",
    [
        "1234/",
        "1337",
        "111111111",
        "1234567890123",
        "C3-PO",
        "R2D2",
    ],
)
def test_cpr_lookup_raises_on_wrong_length(
    service_client: TestClient, cpr_number: str
) -> None:
    response = service_client.request("GET", f"/service/e/cpr_lookup/?q={cpr_number}")
    assert response.status_code == 400
    assert response.json() == {
        "cpr": cpr_number,
        "error_key": "V_CPR_NOT_VALID",
        "description": "Not a valid CPR number.",
        "error": True,
        "status": 400,
    }


@pytest.mark.envvar({"CPR_VALIDATE_BIRTHDATE": "false"})
def test_birthdate_validation_disabled(service_client: TestClient) -> None:
    """Validation of CPR birthdate can be disabled by a feature flag"""
    response = service_client.request("GET", "/service/e/cpr_lookup/?q=0121501234")
    assert response.status_code == 200
    assert response.json() == {}


def _sp_config(monkeypatch, **overrides):
    env_vars = {
        "SP_SERVICE_UUID": SP_UUID,
        "SP_AGREEMENT_UUID": SP_UUID,
        "SP_MUNICIPALITY_UUID": SP_UUID,
        "SP_SYSTEM_UUID": SP_UUID,
        **overrides,
    }
    for env_var, value in env_vars.items():
        monkeypatch.setenv(env_var, value)


def test_serviceplatformen_missing_path(monkeypatch):
    monkeypatch.setenv("ENABLE_SP", "true")
    _sp_config(monkeypatch)

    with pytest.raises(ValueError) as exc_info:
        Settings()
    assert "sp_certificate_path\n  field required" in str(exc_info.value)


def test_serviceplatformen_empty_file(monkeypatch, tmp_path):
    tmp_file = tmp_path / "testfile"
    tmp_file.write_text("")

    monkeypatch.setenv("ENABLE_SP", "true")
    _sp_config(monkeypatch, SP_CERTIFICATE_PATH=str(tmp_file))

    with pytest.raises(ValueError) as exc_info:
        Settings()
    assert "Serviceplatformen certificate can not be empty" in str(exc_info.value)


def test_serviceplatformen_happy_path(monkeypatch, tmp_path):
    tmp_file = tmp_path / "testfile"
    tmp_file.write_text("This is a certificate")

    monkeypatch.setenv("ENVIRONMENT", "production")
    _sp_config(monkeypatch, SP_CERTIFICATE_PATH=str(tmp_file))

    Settings()


@pytest.mark.parametrize(
    "sp_api_version,expected_exception",
    [
        (1, ValueError),
        ("", ValueError),
        (4, None),
        (5, None),
    ],
)
def test_serviceplatformen_api_version_validation(
    monkeypatch,
    sp_configuration,
    sp_api_version,
    expected_exception,
):
    """Test validation in `ServicePlatformenSettings.validate_api_version`"""
    _sp_config(monkeypatch, SP_API_VERSION=str(sp_api_version))
    if expected_exception:
        with pytest.raises(expected_exception):
            Settings()
    else:
        settings = Settings()
        assert settings.sp_settings.sp_api_version == sp_api_version


@pytest.fixture
def sp_certificate(tmp_path: Path) -> Path:
    """Write a throwaway self-signed cert+key PEM and return its path.

    `get_citizen` hands the certificate to `httpx`, which builds its SSL context
    (loading the file) eagerly, so respx needs a real certificate to load before
    it can intercept the request.
    """
    path = tmp_path / "sp.pem"
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "test")])
    certificate = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime(2020, 1, 1))
        .not_valid_after(datetime.datetime(2030, 1, 1))
        .sign(key, hashes.SHA256())
    )
    path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption(),
        )
        + certificate.public_bytes(serialization.Encoding.PEM)
    )
    return path


@pytest.fixture
def sp_enabled(monkeypatch: pytest.MonkeyPatch, sp_certificate: Path) -> None:
    """Enable Serviceplatformen access with a real certificate before the app is built.

    `create_app` reads settings into `app.state.settings` at construction, so the SP
    configuration has to be in the environment before the `service_client` fixture
    builds the app. Requesting this fixture ahead of `service_client` guarantees that.
    """
    monkeypatch.setenv("ENABLE_SP", "true")
    _sp_config(monkeypatch, SP_CERTIFICATE_PATH=str(sp_certificate))


# Minimal SF1520 PersonLookupResponse, just enough for `get_citizen` to parse.
SP_RESPONSE = (
    "<Envelope><Body><PersonLookupResponse>"
    "<persondata><navn><fornavn>John</fornavn><efternavn>Doe</efternavn></navn></persondata>"
    "<adresse><aktuelAdresse></aktuelAdresse></adresse>"
    "<relationer><mor><personnummer>0101010101</personnummer></mor></relationer>"
    "</PersonLookupResponse></Body></Envelope>"
)


def test_get_citizen_uses_version_kwarg(
    respx_mock: respx.MockRouter, sp_certificate: Path
) -> None:
    route = respx_mock.post(
        "https://exttest.serviceplatformen.dk/service/CPR/PersonBaseDataExtended/4"
    ).mock(return_value=httpx.Response(200, text=SP_RESPONSE))

    service_uuids = {
        "service_agreement": "11111111-1111-1111-1111-111111111111",
        "user_system": "22222222-2222-2222-2222-222222222222",
        "user": "33333333-3333-3333-3333-333333333333",
        "service": "44444444-4444-4444-4444-444444444444",
    }
    citizen = serviceplatformen.get_citizen(
        service_uuids, str(sp_certificate), "0101010101", api_version=4
    )

    assert route.called
    assert citizen["fornavn"] == "John"
    assert citizen["efternavn"] == "Doe"


async def test_cpr_lookup_returns_name_from_serviceplatformen(
    sp_enabled: None,
    service_client: TestClient,
    respx_mock: respx.MockRouter,
) -> None:
    """A normal CPR lookup goes through the `get_citizen` shim and returns the name
    parsed from the Serviceplatformen response.
    """
    route = respx_mock.post(
        "https://exttest.serviceplatformen.dk/service/CPR/PersonBaseDataExtended/4"
    ).mock(return_value=httpx.Response(200, text=SP_RESPONSE))

    cpr = "0101501234"
    response = service_client.get("/service/e/cpr_lookup/", params={"q": cpr})

    assert route.called
    assert response.status_code == 200
    assert response.json() == {mapping.NAME: "John Doe", mapping.CPR_NO: cpr}


@pytest.mark.parametrize(
    "cpr_number,expected_result",
    [
        ("invalid", None),
        ("121212333", None),
        ("1212123333", None),
        ("121212-3333", None),
        ("7212123333", {mapping.NAME: "", mapping.CPR_NO: "7212123333"}),
        ("721212-3333", {mapping.NAME: "", mapping.CPR_NO: "721212-3333"}),
    ],
)
def test_handle_erstatningspersonnummer(
    cpr_number: str, expected_result: dict | None
) -> None:
    """Test that we return a valid lookup response in case of fictitious CPRs
    ("erstatningspersonnummer".)
    """
    actual_result = cpr_shim._handle_erstatningspersonnummer(cpr_number)
    assert actual_result == expected_result


@pytest.mark.envvar(
    {
        "CPR_VALIDATE_BIRTHDATE": "false",
        "SP_SERVICE_UUID": SP_UUID,
        "SP_AGREEMENT_UUID": SP_UUID,
        "SP_MUNICIPALITY_UUID": SP_UUID,
        "SP_SYSTEM_UUID": SP_UUID,
    }
)
async def test_cpr_lookup_handles_erstatningspersonnummer(
    sp_configuration: None,
    service_client: TestClient,
) -> None:
    """Test that `search_cpr` handles "erstatningspersonnummer" CPR lookups correctly.

    Looking up an "erstatningspersonnummer" requires the `cpr_validate_birthdate`
    setting to be False, and Serviceplatformen access to be configured.
    Otherwise, `search_cpr` will exit early, returning an empty dict.

    To avoid breaking the contract with client code, we only check for
    "erstatningspersonnummer" CPRs when Serviceplatformen access is available *and* the
    `cpr_validate_birthdate` setting is False.
    """

    cpr = "7202023333"

    # Serviceplatformen access (sp_configuration) and cpr_validate_birthdate=False
    # (envvar marker) are both in place before the app is built, so create_app reads
    # them into app.state.settings.
    response = service_client.request("GET", f"/service/e/cpr_lookup/?q={cpr}")
    assert response.status_code == 200
    assert response.json() == {mapping.NAME: "", mapping.CPR_NO: cpr}
