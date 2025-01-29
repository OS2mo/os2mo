# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import re
from datetime import date
from datetime import datetime
from unittest.mock import AsyncMock
from unittest.mock import patch
from uuid import UUID
from zoneinfo import ZoneInfo

import pytest
from fastapi.encoders import jsonable_encoder
from hypothesis import HealthCheck
from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st
from mora import mapping
from mora.graphapi.shim import execute_graphql
from mora.graphapi.versions.latest.models import EmployeeCreate
from mora.graphapi.versions.latest.models import EmployeeUpdate
from more_itertools import one

from ..conftest import GraphAPIPost

# Helpers

now_beginning = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
tz_cph = ZoneInfo("Europe/Copenhagen")
now_min_cph = datetime.combine(datetime.now().date(), datetime.min.time()).replace(
    tzinfo=tz_cph
)
invalid_uuids = [UUID("7626ad64-327d-481f-8b32-36c78eb12f8c")]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_query_all(graphapi_post: GraphAPIPost):
    """Test that we can query all our employees."""
    query = """
        query {
            employees {
                objects {
                    uuid
                    objects {
                        given_name
                        surname
                        nickname_given_name
                        nickname_surname
                        cpr_number
                        seniority
                        user_key
                        type
                        uuid
                        validity {from to}
                    }
                }
            }
        }
    """
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data


@given(test_data=st.builds(EmployeeCreate))
@patch("mora.graphapi.versions.latest.mutators.create_employee", new_callable=AsyncMock)
async def test_create_employee(
    create_employee: AsyncMock, test_data: EmployeeCreate
) -> None:
    """Test that pydantic jsons are passed through to employee_create."""

    mutate_query = """
        mutation CreateOrgUnit($input: EmployeeCreateInput!) {
            employee_create(input: $input) {
                uuid
            }
        }
    """
    create_employee.return_value = test_data.uuid

    payload = jsonable_encoder(test_data)
    response = await execute_graphql(
        query=mutate_query, variable_values={"input": payload}
    )
    assert response.errors is None
    assert response.data == {"employee_create": {"uuid": str(test_data.uuid)}}

    create_employee.assert_called_with(test_data)


@st.composite
def valid_cprs(draw) -> str:
    # TODO: Add minimum and maximum birthyears as parameters
    valid_date = draw(
        st.dates(
            min_value=date(1970, 1, 1),  # Should really start at 1857
            max_value=date(2057, 1, 1),
        )
    )
    if valid_date.year < 1900:
        # TODO: Add mixed region 5000->9000
        code = draw(st.integers(min_value=5000, max_value=9000))
    elif valid_date.year < 2000:
        # TODO: Add mixed regions 4000->5000, 5000->9000 and 9000+
        code = draw(st.integers(min_value=0, max_value=4000))
    else:
        # TODO: Add mixed regions 4000->5000 and 9000+
        code = draw(st.integers(min_value=9000, max_value=9999))
    valid_code = str(code).zfill(4)
    cpr_number = valid_date.strftime("%d%m%y") + valid_code
    return cpr_number


@settings(
    suppress_health_check=[
        # Running multiple tests on the same database is okay in this instance
        HealthCheck.function_scoped_fixture,
    ],
)
@patch(
    "mora.service.employee.does_employee_with_cpr_already_exist", new_callable=AsyncMock
)
@given(
    test_data=st.builds(
        EmployeeCreate,
        uuid=st.none() | st.uuids(),
        given_name=st.text(
            alphabet=st.characters(whitelist_categories=("L",)), min_size=1
        ),
        surname=st.text(
            alphabet=st.characters(whitelist_categories=("L",)), min_size=1
        ),
        cpr_number=st.none() | valid_cprs(),
    )
)
@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_create_employee_integration_test(
    does_employee_with_cpr_already_exist: AsyncMock,
    test_data: EmployeeCreate,
    graphapi_post: GraphAPIPost,
) -> None:
    """Test that employees can be created in LoRa via GraphQL."""

    does_employee_with_cpr_already_exist.return_value = False

    mutate_query = """
        mutation CreateEmployee($input: EmployeeCreateInput!) {
            employee_create(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post(mutate_query, {"input": jsonable_encoder(test_data)})
    assert response.errors is None
    uuid = UUID(response.data["employee_create"]["uuid"])

    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            employees(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                objects {
                    objects {
                        user_key
                        given_name
                        surname
                        cpr_number
                    }
                }
            }
        }
    """
    response = graphapi_post(verify_query, {"uuid": str(uuid)})
    assert response.errors is None
    obj = one(one(response.data["employees"]["objects"])["objects"])
    assert obj["given_name"] == test_data.given_name
    assert obj["surname"] == test_data.surname
    assert obj["user_key"] == test_data.user_key or str(uuid)
    assert obj["cpr_number"] == test_data.cpr_number


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_create_employee_with_nickname(graphapi_post) -> None:
    """Test that employees can be created with nicknames via GraphQL."""

    mutate_query = """
        mutation CreateEmployee($input: EmployeeCreateInput!) {
            employee_create(input: $input) {
                uuid
                current {
                    nickname_given_name
                    nickname_surname
                    given_name
                    surname
                }
            }
        }
    """
    input = {
        "given_name": "Garik",
        "surname": "Weinstein",
        "nickname_given_name": "Garry",
        "nickname_surname": "Kasparov",
    }
    response = graphapi_post(mutate_query, {"input": input})
    assert response.errors is None
    assert response.data is not None
    UUID(response.data["employee_create"]["uuid"])

    current = response.data["employee_create"]["current"]

    assert current["given_name"] == input["given_name"]
    assert current["surname"] == input["surname"]

    assert current["nickname_given_name"] == input["nickname_given_name"]
    assert current["nickname_surname"] == input["nickname_surname"]


@given(
    st.uuids(),
    # from & to
    st.tuples(st.datetimes(), st.datetimes() | st.none()).filter(
        lambda dts: dts[0] <= dts[1] if dts[0] and dts[1] else True
    ),
    # given_name, surname
    st.tuples(
        st.text() | st.none(),
        st.text() | st.none(),
    ),
    # nickname_given_name, nickname_surname,
    st.tuples(
        st.text() | st.none(),
        st.text() | st.none(),
    ),
    # given_seniority
    # st.text() | st.none(),
    st.datetimes(
        min_value=datetime(1930, 1, 1),
        max_value=now_beginning,
    )
    | st.none(),
    # cpr_number
    # st.from_regex(r"^\d{10}$") | st.none(),
    st.sampled_from(["0101871234", "0102881235"]) | st.none(),
)
async def test_update_mutator(
    given_uuid,
    given_validity_dts,
    given_name_tuple,
    given_nickname_tuple,
    given_seniority,
    given_cpr_number,
) -> None:
    """Test which verifies pydantic values can be sent through the mutator.

    This is done by trying to generate a EmployeeUpdate pydantic class, if this
    succeeds, we also expect the mutator to succeed.. otherwise we expect validation
    errors.
    """

    # Unpack tuples
    given_uuid_str = str(given_uuid)
    given_validity_from, given_validity_to = given_validity_dts
    given_given_name, given_surname = given_name_tuple
    given_nickname_given_name, given_nickname_surname = given_nickname_tuple

    # Create arguments for GraphQL (init with required fields)
    mutator_args = {
        "uuid": given_uuid_str,
        "validity": {"from": given_validity_from.date().isoformat()},
    }

    if given_validity_to:
        mutator_args["validity"]["to"] = given_validity_to.date().isoformat()

    if given_given_name:
        mutator_args["given_name"] = given_given_name
    if given_surname:
        mutator_args["surname"] = given_surname

    if given_nickname_given_name:
        mutator_args["nickname_given_name"] = given_nickname_given_name
    if given_nickname_surname:
        mutator_args["nickname_surname"] = given_nickname_surname

    if given_seniority:
        mutator_args["seniority"] = given_seniority.date().isoformat()
    if given_cpr_number:
        mutator_args["cpr_number"] = given_cpr_number

    # GraphQL
    with patch(
        "mora.graphapi.versions.latest.mutators.update_employee"
    ) as mock_employee_update:
        mock_employee_update.return_value = given_uuid

        query = """
        mutation($input: EmployeeUpdateInput!) {
            employee_update(input: $input) {
                uuid
            }
        }
        """
        response = await execute_graphql(
            query=query, variable_values={"input": mutator_args}
        )

        # Assert
        assert response.errors is None

        response_uuid = None
        if response and response.data:
            response_uuid = response.data.get("employee_update", {}).get("uuid", None)

        assert response_uuid == str(given_uuid)


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "given_mutator_args,given_error_msg_checks",
    [
        # CPR-No
        (
            {"uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a", "cpr_number": ""},
            ["Expected type 'CPR'"],
        ),
        (
            {
                "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                "cpr_number": "00112233445",
            },
            ["Expected type 'CPR'"],
        ),
        (
            {"uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a", "cpr_number": "001122334"},
            ["Expected type 'CPR'"],
        ),
        (
            {"uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a", "cpr_number": "001"},
            ["Expected type 'CPR'"],
        ),
    ],
)
async def test_update_mutator_fails(
    given_mutator_args,
    given_error_msg_checks,
    graphapi_post: GraphAPIPost,
):
    """Test which verifies that certain mutator inputs, cause a validation error."""

    payload = {
        "uuid": given_mutator_args.get("uuid"),
        "validity": {"from": now_min_cph.isoformat()},
        "given_name": given_mutator_args.get("given_name"),
        "surname": given_mutator_args.get("surname"),
        "nickname_given_name": given_mutator_args.get("nickname_given_name"),
        "nickname_surname": given_mutator_args.get("nickname_surname"),
        "seniority": given_mutator_args.get("seniority"),
        "cpr_number": given_mutator_args.get("cpr_number"),
    }

    mutation_response = graphapi_post(
        """
        mutation($input: EmployeeUpdateInput!) {
            employee_update(input: $input) {
                uuid
            }
        }
        """,
        {"input": payload},
    )

    assert mutation_response.errors is not None
    err_message = one(mutation_response.errors).get("message", "")

    for error_msg_check in given_error_msg_checks:
        assert re.search(error_msg_check, err_message)


@pytest.mark.parametrize(
    "given_data",
    [
        {
            "uuid": UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a"),
            "user_key": "a-new-test-userkey",
        },
        {
            "uuid": UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a"),
            "given_name": "Test Given Name",
        },
        {
            "uuid": UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a"),
            "surname": "Duke",
        },
        {
            "uuid": UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a"),
            "nickname_given_name": "Fancy Nickname Given Name",
        },
        {
            "uuid": UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a"),
            "nickname_surname": "Lord Nick",
        },
        {
            "uuid": UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a"),
            "seniority": now_min_cph.date().isoformat(),
        },
        {
            "uuid": UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a"),
            "cpr_number": "0101892147",
        },
        {
            "uuid": UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a"),
            "given_name": "TestMan",
            "surname": "Duke",
            "nickname_given_name": "Test",
            "nickname_surname": "Lord",
            "seniority": now_min_cph.date().isoformat(),
            "cpr_number": "0101872144",
        },
    ],
)
@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_update_integration(given_data, graphapi_post: GraphAPIPost):
    # Create test data
    test_data = EmployeeUpdate(
        uuid=given_data.get("uuid"),
        user_key=given_data.get("user_key"),
        validity={"from": now_min_cph},
        given_name=given_data.get("given_name"),
        surname=given_data.get("surname"),
        nickname_given_name=given_data.get("nickname_given_name"),
        nickname_surname=given_data.get("nickname_surname"),
        seniority=given_data.get("seniority"),
        cpr_number=given_data.get("cpr_number"),
    )
    payload = jsonable_encoder(test_data)

    # Invoke mutation & and get updated employee UUID
    mutation_response = graphapi_post(
        """
        mutation($input: EmployeeUpdateInput!) {
            employee_update(input: $input) {
                uuid
            }
        }
        """,
        {"input": payload},
    )
    assert mutation_response.errors is None
    test_data_uuid_updated = UUID(mutation_response.data["employee_update"]["uuid"])

    # Fetch employee and verify and updated version of the employee can be found
    verify_response = graphapi_post(
        _get_employee_verify_query(), {mapping.UUID: str(test_data_uuid_updated)}
    )
    assert verify_response.errors is None
    assert len(verify_response.data["employees"]["objects"]) > 0

    verify_data_employee = one(verify_response.data["employees"]["objects"])
    verify_data_employee_objs = verify_data_employee.get("objects", [])
    assert len(verify_data_employee_objs) > 1

    verify_data = None
    for e_obj in verify_data_employee_objs:
        if not e_obj.get("validity", {}).get("to"):
            verify_data = e_obj
            break
    assert verify_data is not None

    # Assert the employee have been updated with the specified test data
    if test_data.user_key:
        assert verify_data.get("user_key") == test_data.user_key

    if test_data.given_name:
        assert verify_data.get("given_name") == test_data.given_name

    if test_data.surname:
        assert verify_data.get("surname") == test_data.surname

    if test_data.seniority:
        assert verify_data.get("seniority") == test_data.seniority.isoformat()

    if test_data.cpr_number:
        assert verify_data.get("cpr_number") == test_data.cpr_number


def _get_lora_mutator_arg(mutator_key: str, lora_employee: dict):
    """Finds LoRa-employee equivalent value to a employee-update mutation argument.

    IMPORTANT: lora-employee attributes & relations are lists of objects with all
    attributes, which all have a "from" and "to", to specify if "the set of attributes"
    is active. The way this method finds the active ones are just by looking for an
    object where "to" is set to the string: "infinity".>
    """
    if not lora_employee:
        return None

    # Find expansion by finding the one where to==infinity
    employee_expansions = lora_employee.get("attributter", {}).get(
        "brugerudvidelser", []
    )
    active_expansion = None
    for expansion in employee_expansions:
        expansion_to = expansion.get("virkning", {}).get("to", None)
        if expansion_to != mapping.INFINITY:
            continue

        active_expansion = expansion
        break

    # Find associated people (for CPR no) by finding the one where to==infinity
    employee_associated_people = lora_employee.get("relationer", {}).get(
        "tilknyttedepersoner", []
    )
    employee_associated_people_active = None
    for asso_ppl in employee_associated_people:
        to_date = asso_ppl.get("virkning", {}).get("to", None)
        if not to_date or to_date != mapping.INFINITY:
            continue

        employee_associated_people_active = asso_ppl
        break

    # Find mutator key equivalent
    if mutator_key == "from_date":
        from_date_str = lora_employee.get("fratidspunkt", {}).get(
            "tidsstempeldatotid", None
        )
        return datetime.fromisoformat(from_date_str)

    if mutator_key == "name":
        return f"{active_expansion['fornavn']} {active_expansion['efternavn']}"

    if mutator_key == "given_name":
        return active_expansion["fornavn"]

    if mutator_key == "surname":
        return active_expansion["efternavn"]

    if mutator_key == "nickname":
        return f"{active_expansion['kaldenavn_fornavn']} {active_expansion['kaldenavn_efternavn']}"

    if mutator_key == "nickname_given_name":
        return active_expansion["kaldenavn_fornavn"]

    if mutator_key == "nickname_surname":
        return active_expansion["kaldenavn_efternavn"]

    if mutator_key == "seniority":
        return active_expansion["seniority"]

    if mutator_key == "cpr_number":
        cpr_number = employee_associated_people_active.get("urn", "").split(":")[-1]
        return cpr_number if len(cpr_number) > 0 else None

    return None


def _get_employee_verify_query():
    return """
        query VerifyQuery($uuid: UUID!) {
          employees(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
            objects {
              uuid,
              objects {
                uuid
                user_key
                given_name
                surname
                nickname_given_name
                nickname_surname
                seniority
                cpr_number
                validity {
                  from
                  to
                }
              }
            }
          }
        }
    """
