# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from fastapi.testclient import TestClient

from . import util
from mora.config import Settings


@pytest.mark.parametrize(
    "cpr_number",
    [
        "1234/",
        "1337",
        "111111111",
        "1234567890123",
        "2222222222",
        "C3-PO",
        "R2D2",
    ],
)
def test_cpr_lookup_raises_on_wrong_length(
    service_client: TestClient, cpr_number: str
) -> None:
    response = service_client.get(f"/service/e/cpr_lookup/?q={cpr_number}")
    assert response.status_code == 400
    assert response.json() == {
        "cpr": cpr_number,
        "error_key": "V_CPR_NOT_VALID",
        "description": "Not a valid CPR number.",
        "error": True,
        "status": 400,
    }


def test_birthdate_validation_disabled(service_client: TestClient) -> None:
    """Validation of CPR birthdate can be disabled by a feature flag"""
    with util.override_config(Settings(cpr_validate_birthdate=False)):
        response = service_client.get("/service/e/cpr_lookup/?q=0121501234")
        assert response.status_code == 200
        assert response.json() == {"name": "Naja Hansen", "cpr_no": "0121501234"}


def _sp_config(monkeypatch, **overrides):
    UUID_OK = "12345678-9abc-def1-1111-111111111111"

    env_vars = {
        "SP_SERVICE_UUID": UUID_OK,
        "SP_AGREEMENT_UUID": UUID_OK,
        "SP_MUNICIPALITY_UUID": UUID_OK,
        "SP_SYSTEM_UUID": UUID_OK,
        **overrides,
    }
    for env_var, value in env_vars.items():
        monkeypatch.setenv(env_var, value)


def test_serviceplatformen_missing_path(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    _sp_config(monkeypatch)

    with pytest.raises(ValueError) as exc_info:
        Settings()
    assert "sp_certificate_path\n  field required" in str(exc_info.value)


def test_serviceplatformen_empty_file(monkeypatch, tmp_path):
    tmp_file = tmp_path / "testfile"
    tmp_file.write_text("")

    monkeypatch.setenv("ENVIRONMENT", "production")
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
