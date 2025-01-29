# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from fastapi.testclient import TestClient
from mora import app
from mora.service import org
from starlette.responses import JSONResponse


class TestServiceApp:
    async def test_fallback_handler(self):
        resp = await app.fallback_handler(ValueError("go away"))
        assert isinstance(resp, JSONResponse)
        assert resp.status_code == 500
        assert (
            resp.body == b'{"error":true,"description":"go away",'
            b'"status":500,"error_key":"E_UNKNOWN"}'
        )

    def test_failing_service(self, service_client: TestClient):
        response = service_client.request("GET", "/service/kaflaflibob")
        assert response.status_code == 404
        assert response.json() == {
            "error": True,
            "error_key": "E_NO_SUCH_ENDPOINT",
            "description": "No such endpoint.",
            "status": 404,
        }

    def test_exception_handling(
        self, service_client_not_raising: TestClient, monkeypatch
    ):
        def raise_value_error():
            raise ValueError("ARGH")

        monkeypatch.setattr(org, "get_configured_organisation", raise_value_error)
        response = service_client_not_raising.get("/service/o/")
        assert response.status_code == 500
        assert response.json() == {
            "error": True,
            "description": "ARGH",
            "status": 500,
            "error_key": "E_UNKNOWN",
        }
