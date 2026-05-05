# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import datetime
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from mora import exceptions
from mora import mapping
from mora import util as mora_util
from mora.service.validation import validator

from tests.util import set_settings_contextmanager


@pytest.fixture(autouse=True)
def patch_context(monkeypatch):
    """Fixture for patching the Starlette context.

    autouse=True makes the fixture run on every test in the file
    """
    monkeypatch.setattr(mora_util, "context", {"query_args": {}})
    yield


ORG = "456362c4-0ee4-4e5e-a72c-751239745e62"
SAMF_UNIT = "b688513d-11f7-4efc-b679-ab082a2055d0"
HIST_UNIT = "da77153e-30f3-4dc2-a611-ee912a28d8aa"
PARENT = SAMF_UNIT


def expire_org_unit(service_client: TestClient, org_unit: dict) -> None:
    # Expire the parent from 2018-01-01
    payload = {"validity": {"to": "2018-01-01"}}

    response = service_client.request(
        "POST", f"/service/ou/{org_unit}/terminate", json=payload
    )
    # amqp_topics={"org_unit.org_unit.delete": 1},
    assert response.status_code == 200
    assert response.json() == org_unit


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_should_return_true_when_interval_contained(
    service_client: TestClient,
) -> None:
    """
    [------ super ------)
       [--- sub ---)
    """
    expire_org_unit(service_client, PARENT)

    startdate = "01-02-2017"
    enddate = "01-06-2017"

    await validator.is_date_range_in_org_unit_range(
        {"uuid": PARENT},
        mora_util.parsedatetime(startdate),
        mora_util.parsedatetime(enddate),
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_should_return_true_when_interval_contained2(
    service_client: TestClient,
) -> None:
    """
    [------ super ------)
    [------ sub ---)
    """
    expire_org_unit(service_client, PARENT)

    startdate = "01-01-2017"
    enddate = "01-06-2017"

    await validator.is_date_range_in_org_unit_range(
        {"uuid": PARENT},
        mora_util.parsedatetime(startdate),
        mora_util.parsedatetime(enddate),
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_should_return_true_when_interval_contained3(
    service_client: TestClient,
) -> None:
    """
    [------ super ------)
      [------ sub ------)
    """
    expire_org_unit(service_client, PARENT)

    startdate = "01-02-2017"
    enddate = "01-01-2018"

    await validator.is_date_range_in_org_unit_range(
        {"uuid": PARENT},
        mora_util.parsedatetime(startdate),
        mora_util.parsedatetime(enddate),
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_should_false_true_when_interval_not_contained1(
    service_client: TestClient,
) -> None:
    """
      [---- super ------)
    [------ sub ---)
    """
    expire_org_unit(service_client, PARENT)

    startdate = "01-01-2016"
    enddate = "01-06-2017"

    with pytest.raises(exceptions.HTTPException):
        await validator.is_date_range_in_org_unit_range(
            {"uuid": PARENT},
            mora_util.parsedatetime(startdate),
            mora_util.parsedatetime(enddate),
        )


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_should_return_false_when_interval_not_contained2(
    service_client: TestClient,
) -> None:
    """
    [------ super ------)
      [---- sub -----------)
    """
    expire_org_unit(service_client, PARENT)

    startdate = "01-02-2017"
    enddate = "01-06-2019"

    with pytest.raises(exceptions.HTTPException):
        await validator.is_date_range_in_org_unit_range(
            {"uuid": PARENT},
            mora_util.parsedatetime(startdate),
            mora_util.parsedatetime(enddate),
        )


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_should_return_false_when_interval_not_contained3(
    service_client: TestClient,
) -> None:
    """
                               [------ super ------)
    [---- sub -----------)
    """
    expire_org_unit(service_client, PARENT)

    startdate = "01-02-2010"
    enddate = "01-06-2015"

    with pytest.raises(exceptions.HTTPException):
        await validator.is_date_range_in_org_unit_range(
            {"uuid": PARENT},
            mora_util.parsedatetime(startdate),
            mora_util.parsedatetime(enddate),
        )


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_is_date_range_in_employee_valid_raises_outside_range() -> None:
    """Assert that a validation error is raised when the range exceeds
    employee range"""

    # Arrange
    employee_uuid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"  # Anders And
    valid_from = mora_util.parsedatetime("1910-01-01")
    valid_to = mora_util.parsedatetime("2040-01-01")
    employee = {"uuid": employee_uuid}

    # Act & Assert
    with pytest.raises(exceptions.HTTPException):
        await validator.is_date_range_in_employee_range(employee, valid_from, valid_to)


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_is_date_range_in_employee_valid_inside_range() -> None:
    """Assert that a validation error is not raised when the range is
    inside employee range"""

    # Arrange
    employee_uuid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"  # Anders And
    valid_from = mora_util.parsedatetime("2020-01-01")
    valid_to = mora_util.parsedatetime("2040-01-01")
    employee = {"uuid": employee_uuid}

    # Act & Assert
    # Should be callable without raising exception
    await validator.is_date_range_in_employee_range(employee, valid_from, valid_to)


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_is_distinct_responsibility_with_duplicate() -> None:
    with pytest.raises(exceptions.HTTPException) as ctxt:
        validator.is_distinct_responsibility(
            [
                (
                    mapping.RESPONSIBILITY_FIELD,
                    {
                        "objekttype": "lederansvar",
                        "uuid": "00000000-0000-0000-0000-000000000000",
                    },
                ),
                (
                    mapping.RESPONSIBILITY_FIELD,
                    {
                        "objekttype": "lederansvar",
                        "uuid": "00000000-0000-0000-0000-000000000000",
                    },
                ),
                (
                    mapping.RESPONSIBILITY_FIELD,
                    {
                        "objekttype": "lederansvar",
                        "uuid": "00000000-0000-0000-0000-000000000001",
                    },
                ),
            ]
        )

    assert ctxt.value.detail == {
        "description": "Manager has the same responsibility more than once.",
        "duplicates": ["00000000-0000-0000-0000-000000000000"],
        "error": True,
        "error_key": "V_DUPLICATED_RESPONSIBILITY",
        "status": 400,
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_is_distinct_responsibility_no_duplicate() -> None:
    validator.is_distinct_responsibility(
        [
            (
                mapping.RESPONSIBILITY_FIELD,
                {
                    "objekttype": "lederansvar",
                    "uuid": "00000000-0000-0000-0000-000000000000",
                },
            ),
            (
                mapping.RESPONSIBILITY_FIELD,
                {
                    "objekttype": "lederansvar",
                    "uuid": "00000000-0000-0000-0000-000000000001",
                },
            ),
            (
                mapping.MANAGER_LEVEL_FIELD,
                {
                    "objekttype": "hestefest",
                    "uuid": "00000000-0000-0000-0000-000000000001",
                },
            ),
        ]
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@set_settings_contextmanager(
    confdb_substitute_roles='["bcd05828-cc10-48b1-bc48-2f0d204859b2"]'
)
def test_is_substitute_allowed() -> None:
    # This should pass
    validator.is_substitute_allowed(UUID("bcd05828-cc10-48b1-bc48-2f0d204859b2"))

    # This shouldn't
    with pytest.raises(exceptions.HTTPException):
        validator.is_substitute_allowed(UUID("8b073375-4196-4d90-9af9-0eb6ef8b6d0d"))


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_is_substitute_self() -> None:
    # This should pass
    validator.is_substitute_self(
        "32eba675-1edb-4c08-8d1a-82caf948aae6",
        "962f70a7-4cb0-47f8-b949-ec249c595936",
    )

    # This shouldn't
    with pytest.raises(exceptions.HTTPException):
        validator.is_substitute_self(
            "8b073375-4196-4d90-9af9-0eb6ef8b6d0d",
            "8b073375-4196-4d90-9af9-0eb6ef8b6d0d",
        )


UNIT_TO_MOVE = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"  # Hum


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_cannot_move_unit_to_own_subtree() -> None:
    candidate_parent = "04c78fc2-72d2-4d02-b55f-807af19eac48"  # Frem

    move_date = "01-02-2017"
    new_org_uuid = candidate_parent

    with pytest.raises(exceptions.HTTPException):
        await validator.is_candidate_parent_valid(UNIT_TO_MOVE, new_org_uuid, move_date)


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_should_allow_move_unit_to_valid_orgtree_location() -> None:
    candidate_parent = "b688513d-11f7-4efc-b679-ab082a2055d0"  # Samf

    move_date = "01-02-2017"
    new_org_uuid = candidate_parent

    # Should not raise
    await validator.is_candidate_parent_valid(UNIT_TO_MOVE, new_org_uuid, move_date)


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_should_not_move_root_org_unit() -> None:
    root_org_unit = "2874e1dc-85e6-4269-823a-e1125484dfd3"
    candidate_parent = "b688513d-11f7-4efc-b679-ab082a2055d0"  # Samf

    move_date = "01-02-2017"
    new_org_uuid = candidate_parent

    with pytest.raises(exceptions.HTTPException):
        await validator.is_candidate_parent_valid(
            root_org_unit, new_org_uuid, move_date
        )


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_should_not_move_org_unit_to_child() -> None:
    candidate_parent = "85715fc7-925d-401b-822d-467eb4b163b6"  # Fil

    move_date = "01-02-2017"
    new_org_uuid = candidate_parent

    with pytest.raises(exceptions.HTTPException):
        await validator.is_candidate_parent_valid(UNIT_TO_MOVE, new_org_uuid, move_date)


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_should_not_move_org_unit_to_itself() -> None:
    move_date = "01-02-2017"

    with pytest.raises(exceptions.HTTPException):
        await validator.is_candidate_parent_valid(UNIT_TO_MOVE, UNIT_TO_MOVE, move_date)


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_should_return_false_when_candidate_parent_is_inactive(
    service_client: TestClient,
) -> None:
    move_date = "01-01-2019"
    new_org_uuid = PARENT

    expire_org_unit(service_client, PARENT)

    with pytest.raises(exceptions.HTTPException):
        await validator.is_candidate_parent_valid(UNIT_TO_MOVE, new_org_uuid, move_date)


@pytest.mark.parametrize(
    "empl_from,empl_to,valid_from,valid_to",
    [
        # upper
        (
            datetime.date(2010, 1, 1),
            datetime.date(2018, 1, 1),
            datetime.date(2012, 1, 1),
            datetime.date(2020, 1, 1),
        ),
        # lower
        (
            datetime.date(2010, 1, 1),
            datetime.date(2018, 1, 1),
            datetime.date(2008, 1, 1),
            datetime.date(2016, 1, 1),
        ),
    ],
)
def test_raises_when_outside_range_upper(
    empl_from, empl_to, valid_from, valid_to
) -> None:
    with pytest.raises(exceptions.HTTPException):
        validator.is_contained_in_range(
            empl_from,
            empl_to,
            valid_from,
            valid_to,
            exceptions.ErrorCodes.V_DATE_OUTSIDE_EMPL_RANGE,
        )


def test_passes_when_inside_range() -> None:
    empl_from = datetime.date(2010, 1, 1)
    empl_to = datetime.date(2018, 1, 1)

    valid_from = datetime.date(2010, 1, 1)
    valid_to = datetime.date(2018, 1, 1)

    # Should not raise an exception
    validator.is_contained_in_range(
        empl_from,
        empl_to,
        valid_from,
        valid_to,
        exceptions.ErrorCodes.V_DATE_OUTSIDE_EMPL_RANGE,
    )
