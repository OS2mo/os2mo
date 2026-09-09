# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import httpx
import pytest
import respx
from more_itertools import one

from tests.conftest import SP_CERTIFICATE_PATH
from tests.conftest import SP_RESPONSE
from tests.conftest import SP_UUID
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth

SP_ENABLED_SETTINGS = {
    "ENABLE_SP": "true",
    "SP_SERVICE_UUID": SP_UUID,
    "SP_AGREEMENT_UUID": SP_UUID,
    "SP_MUNICIPALITY_UUID": SP_UUID,
    "SP_SYSTEM_UUID": SP_UUID,
    "SP_CERTIFICATE_PATH": SP_CERTIFICATE_PATH,
}

SP_URL = "https://exttest.serviceplatformen.dk/service/CPR/PersonBaseDataExtended/4"

CPR_QUERY = """
    query TestQuery($cpr_number: String!) {
        cpr(filter: {cpr_number: $cpr_number}) {
            name
            cpr_number
        }
    }
"""


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_cpr_lookup_disabled(graphapi_post: GraphAPIPost) -> None:
    """With Serviceplatformen disabled, lookups fail with an error."""
    response = graphapi_post(CPR_QUERY, {"cpr_number": "0101501234"})

    assert response.errors is not None
    assert one(response.errors)["message"] == (
        "CPR number lookup is not possible, because the 'serviceplatformen' "
        "integration is disabled."
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.envvar(SP_ENABLED_SETTINGS)
async def test_cpr_lookup_invalid_cpr(graphapi_post: GraphAPIPost) -> None:
    """An invalid CPR number fails with an error."""
    response = graphapi_post(CPR_QUERY, {"cpr_number": "1234"})

    assert response.errors is not None
    assert one(response.errors)["message"] == "The given CPR number is not valid."


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.envvar({**SP_ENABLED_SETTINGS, "CPR_VALIDATE_BIRTHDATE": "false"})
async def test_cpr_lookup_erstatningspersonnummer(
    graphapi_post: GraphAPIPost,
) -> None:
    """Fictitious "erstatningspersonnummer" CPR numbers are handled without hitting Serviceplatformen."""
    response = graphapi_post(CPR_QUERY, {"cpr_number": "7212123333"})

    assert response.errors is None
    assert response.data == {
        "cpr": {
            "name": "",
            "cpr_number": "7212123333",
        }
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.envvar(SP_ENABLED_SETTINGS)
async def test_cpr_lookup_returns_name(
    graphapi_post: GraphAPIPost,
    respx_mock: respx.MockRouter,
) -> None:
    """A normal CPR lookup queries Serviceplatformen and returns the person's name."""
    route = respx_mock.post(SP_URL).mock(
        return_value=httpx.Response(200, text=SP_RESPONSE)
    )

    response = graphapi_post(CPR_QUERY, {"cpr_number": "0101501234"})

    assert route.called
    assert response.errors is None
    assert response.data == {
        "cpr": {
            "name": "John Doe",
            "cpr_number": "0101501234",
        }
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.envvar(SP_ENABLED_SETTINGS)
async def test_cpr_lookup_not_found(
    graphapi_post: GraphAPIPost,
    respx_mock: respx.MockRouter,
) -> None:
    """A `PNRNotFound` Serviceplatformen error fails with an error."""
    route = respx_mock.post(SP_URL).mock(
        return_value=httpx.Response(500, text="<faultstring>PNRNotFound</faultstring>")
    )

    response = graphapi_post(CPR_QUERY, {"cpr_number": "0101501234"})

    assert route.called
    assert response.errors is not None
    assert one(response.errors)["message"] == (
        "No person was found that matches the given CPR number."
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.envvar(SP_ENABLED_SETTINGS)
@pytest.mark.parametrize(
    "exception",
    [
        httpx.ConnectError("boom"),
        httpx.TimeoutException("boom"),
    ],
)
async def test_cpr_lookup_unavailable(
    graphapi_post: GraphAPIPost,
    respx_mock: respx.MockRouter,
    exception: Exception,
) -> None:
    """An unreachable Serviceplatformen fails with an error."""
    route = respx_mock.post(SP_URL).mock(side_effect=exception)

    response = graphapi_post(CPR_QUERY, {"cpr_number": "0101501234"})

    assert route.called
    assert response.errors is not None
    assert one(response.errors)["message"] == (
        "CPR number lookup is not possible, because the 'serviceplatformen' "
        "integration could not be reached."
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "roles, access_denied",
    [
        (set(), True),
        ({"reader"}, False),
    ],
)
async def test_cpr_rbac(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    roles: set[str],
    access_denied: bool,
) -> None:
    """The `cpr` query requires the `reader` role."""
    set_auth(roles, None)

    response = graphapi_post(CPR_QUERY, {"cpr_number": "0101501234"})

    error_messages = (
        {error["message"] for error in response.errors} if response.errors else set()
    )
    if access_denied:
        assert "No policy approved the access" in error_messages
    else:
        assert "No policy approved the access" not in error_messages
