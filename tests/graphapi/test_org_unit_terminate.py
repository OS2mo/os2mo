# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from uuid import uuid4

import pytest

from mora.exceptions import ErrorCodes
from mora.exceptions import HTTPException
from mora.service.validation import validator
from mora.util import DEFAULT_TIMEZONE
from tests.conftest import GraphAPIPost

TERMINATE_MUTATION = """
    mutation TerminateOrgUnit($input: OrganisationUnitTerminateInput!) {
        org_unit_terminate(input: $input) { uuid }
    }
"""


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_terminate_org_unit_with_roles(
    graphapi_post: GraphAPIPost,
    create_org_unit,
    create_person,
    create_engagement,
) -> None:
    """Terminating a unit with an active role is rejected."""
    org_unit_uuid = create_org_unit("with-roles")
    person_uuid = create_person({"given_name": "Xylia", "surname": "Shadowthorn"})
    create_engagement(
        {
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "org_unit": str(org_unit_uuid),
            "person": str(person_uuid),
            "validity": {"from": "1970-01-01T00:00:00Z"},
        }
    )

    response = graphapi_post(
        TERMINATE_MUTATION,
        {"input": {"uuid": str(org_unit_uuid), "to": "2020-01-01"}},
    )
    assert response.errors is not None
    assert (
        response.errors[0]["extensions"]["error_context"]["error_key"]
        == "V_TERMINATE_UNIT_WITH_ROLES"
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_terminate_org_unit_with_children_and_roles(
    graphapi_post: GraphAPIPost,
    create_org_unit,
    create_person,
    create_engagement,
) -> None:
    """Terminating a unit with both children and roles is rejected."""
    parent_uuid = create_org_unit("parent")
    create_org_unit("child", parent=parent_uuid)
    person_uuid = create_person({"given_name": "Xylia", "surname": "Shadowthorn"})
    create_engagement(
        {
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "org_unit": str(parent_uuid),
            "person": str(person_uuid),
            "validity": {"from": "1970-01-01T00:00:00Z"},
        }
    )

    response = graphapi_post(
        TERMINATE_MUTATION,
        {"input": {"uuid": str(parent_uuid), "to": "2020-01-01"}},
    )
    assert response.errors is not None
    assert (
        response.errors[0]["extensions"]["error_context"]["error_key"]
        == "V_TERMINATE_UNIT_WITH_CHILDREN_AND_ROLES"
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_is_candidate_parent_valid_rejects_inactive_parent(
    graphapi_post: GraphAPIPost,
    create_org_unit,
) -> None:
    """Moving a unit under a terminated parent is rejected."""
    unit_to_move_uuid = create_org_unit("to-move")
    target_parent_uuid = create_org_unit("inactive-parent")

    response = graphapi_post(
        TERMINATE_MUTATION,
        {"input": {"uuid": str(target_parent_uuid), "to": "2020-01-01"}},
    )
    assert response.errors is None

    with pytest.raises(HTTPException) as excinfo:
        await validator.is_candidate_parent_valid(
            str(unit_to_move_uuid),
            str(target_parent_uuid),
            datetime(2025, 1, 1, tzinfo=DEFAULT_TIMEZONE),
        )
    assert excinfo.value.key == ErrorCodes.V_DATE_OUTSIDE_ORG_UNIT_RANGE
