# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import httpx
import pytest
import respx

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
            ... on CPRPerson {
                name
                cpr_number
            }
            ... on CPRError {
                reason
                cpr_number
            }
        }
    }
"""


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_cpr_lookup_disabled(graphapi_post: GraphAPIPost) -> None:
    """With Serviceplatformen disabled, lookups fail with `SERVICEPLATFORMEN_DISABLED`."""
    response = graphapi_post(CPR_QUERY, {"cpr_number": "0101501234"})

    assert response.errors is None
    assert response.data == {
        "cpr": {
            "reason": "SERVICEPLATFORMEN_DISABLED",
            "cpr_number": "0101501234",
        }
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.envvar(SP_ENABLED_SETTINGS)
async def test_cpr_lookup_invalid_cpr(graphapi_post: GraphAPIPost) -> None:
    """An invalid CPR number fails with `INVALID_CPR_NUMBER`."""
    response = graphapi_post(CPR_QUERY, {"cpr_number": "1234"})

    assert response.errors is None
    assert response.data == {
        "cpr": {
            "reason": "INVALID_CPR_NUMBER",
            "cpr_number": "1234",
        }
    }


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
    """A `PNRNotFound` Serviceplatformen error fails with `PERSON_NOT_FOUND`."""
    route = respx_mock.post(SP_URL).mock(
        return_value=httpx.Response(500, text="<faultstring>PNRNotFound</faultstring>")
    )

    response = graphapi_post(CPR_QUERY, {"cpr_number": "0101501234"})

    assert route.called
    assert response.errors is None
    assert response.data == {
        "cpr": {
            "reason": "PERSON_NOT_FOUND",
            "cpr_number": "0101501234",
        }
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.envvar(SP_ENABLED_SETTINGS)
async def test_cpr_lookup_unavailable(
    graphapi_post: GraphAPIPost,
    respx_mock: respx.MockRouter,
) -> None:
    """An unreachable Serviceplatformen fails with `SERVICEPLATFORMEN_UNAVAILABLE`."""
    route = respx_mock.post(SP_URL).mock(side_effect=httpx.ConnectError("boom"))

    response = graphapi_post(CPR_QUERY, {"cpr_number": "0101501234"})

    assert route.called
    assert response.errors is None
    assert response.data == {
        "cpr": {
            "reason": "SERVICEPLATFORMEN_UNAVAILABLE",
            "cpr_number": "0101501234",
        }
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "roles, expected_errors",
    [
        (set(), {"No policy approved the access"}),
        ({"reader"}, set()),
    ],
)
async def test_cpr_rbac(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    roles: set[str],
    expected_errors: set[str],
) -> None:
    """The `cpr` query requires the `reader` role."""
    set_auth(roles, None)

    response = graphapi_post(CPR_QUERY, {"cpr_number": "0101501234"})

    error_messages = (
        {error["message"] for error in response.errors} if response.errors else set()
    )
    assert expected_errors == error_messages
