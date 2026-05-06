# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import AsyncMock
from unittest.mock import patch

from mora import util as mora_util

UUID = {"uuid": "be0df80c-7eed-4a2e-a682-e36be4e4877e"}
FROM_DATE = "2000-01-01"
PERSON_UUID = "cc1fc948-d3f6-4bbc-9faf-288e0f956135"
ORG_UNIT_UUID = "f4f28810-cdd9-4ff5-821e-427378ab4bf7"


@patch("mora.service.validate.validator.is_date_range_in_org_unit_range")
def test_candidate_org_unit(mock, service_client):
    payload = {
        "org_unit": UUID,
        "validity": {"from": FROM_DATE, "to": None},
    }

    service_client.request("POST", "/service/validate/org-unit/", json=payload)

    mock.assert_called_with(
        UUID,
        mora_util.parsedatetime(FROM_DATE),
        mora_util.POSITIVE_INFINITY,
    )


@patch("mora.service.validate.validator.is_date_range_in_employee_range")
def test_validate_employee(mock, service_client):
    payload = {
        "person": UUID,
        "validity": {"from": FROM_DATE, "to": None},
    }

    service_client.request("POST", "/service/validate/employee/", json=payload)

    mock.assert_called_with(
        UUID,
        mora_util.parsedatetime(FROM_DATE),
        mora_util.POSITIVE_INFINITY,
    )


@patch("mora.service.validate.validator.does_employee_with_cpr_already_exist")
def test_cpr(mock, service_client):
    cpr_no = "1234567890"

    org_uuid = "52e8d1ff-6fe0-4e8a-a19c-8bd8e1154b3b"
    payload = {"cpr_no": cpr_no, "org": {"uuid": org_uuid}}

    service_client.request("POST", "/service/validate/cpr/", json=payload)

    mock.assert_called_with(
        cpr_no, mora_util.NEGATIVE_INFINITY, mora_util.POSITIVE_INFINITY, org_uuid
    )


@patch("mora.service.validate.validator.does_employee_have_active_engagement")
def test_employee_engagements(mock, service_client):
    payload = {
        "person": {"uuid": PERSON_UUID},
        "validity": {"from": FROM_DATE, "to": None},
    }

    service_client.request(
        "POST", "/service/validate/active-engagements/", json=payload
    )
    mock.assert_called_with(
        PERSON_UUID,
        mora_util.parsedatetime(FROM_DATE),
        mora_util.POSITIVE_INFINITY,
    )


@patch("mora.service.validate.validator.does_employee_have_existing_association")
def test_existing_associations(mock, service_client):
    association_uuid = "7cd87e2a-e41a-4b68-baca-ff69426be753"
    payload = {
        "person": {"uuid": PERSON_UUID},
        "org_unit": {"uuid": ORG_UNIT_UUID},
        "validity": {"from": FROM_DATE, "to": None},
        "uuid": association_uuid,
    }

    service_client.request(
        "POST", "/service/validate/existing-associations/", json=payload
    )
    mock.assert_called_with(
        PERSON_UUID,
        ORG_UNIT_UUID,
        mora_util.parsedatetime(FROM_DATE),
        association_uuid,
    )


@patch("mora.service.validate.validator.is_candidate_parent_valid")
def test_parent_org_unit(mock, service_client):
    parent_uuid = "cc1fc948-d3f6-4bbc-9faf-288e0f956135"

    payload = {
        "org_unit": {"uuid": ORG_UNIT_UUID},
        "parent": {"uuid": parent_uuid},
        "validity": {
            "from": FROM_DATE,
        },
    }

    service_client.request(
        "POST", "/service/validate/candidate-parent-org-unit/", json=payload
    )

    mock.assert_called_with(
        ORG_UNIT_UUID, parent_uuid, mora_util.parsedatetime(FROM_DATE)
    )


@patch("mora.service.address_handler.base.get_handler_for_scope")
@patch("mora.service.facet.get_one_class")
def test_address(get_one_class, get_handler_for_scope, service_client):
    value = "12341234"
    scope = "SCOPE"

    payload = {
        "address_type": {"uuid": "cc1fc948-d3f6-4bbc-9faf-288e0f956135"},
        "value": value,
    }
    get_one_class.return_value = {"scope": scope}
    get_handler_for_scope.return_value = handler = AsyncMock()

    service_client.request("POST", "/service/validate/address/", json=payload)

    get_handler_for_scope.assert_called_with(scope)
    handler.validate_value.assert_called_with(value)
