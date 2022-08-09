#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import datetime
import json
from itertools import product
from typing import Optional
from typing import Tuple
from uuid import UUID

import pytest
from parameterized import parameterized
from pydantic.error_wrappers import ValidationError
from ramodels.mo.organisation_unit import OrganisationUnitTerminate

import tests.cases
from mora import mapping
from mora.exceptions import ErrorCodes
from mora.exceptions import HTTPException
from mora.service.orgunit import OrgUnitRequestHandler
from mora.service.orgunit import terminate_org_unit_validation


async def terminate_orgunit(
    orgunit_id: UUID,
    from_date: Optional[datetime.date],
    to_date: Optional[datetime.date],
):
    _ = OrganisationUnitTerminate(
        validity={
            mapping.FROM: from_date.isoformat() if from_date else None,
            mapping.TO: to_date.isoformat() if to_date else None,
        }
    )

    # Create payload of old terminate logic
    uuid_str = str(orgunit_id)

    request_dict = {
        mapping.UUID: uuid_str,
        mapping.VALIDITY: {
            mapping.FROM: from_date.isoformat() if from_date else None,
            mapping.TO: to_date.isoformat() if to_date else None,
        },
    }

    # Old terminate logic
    if not request_dict[mapping.VALIDITY][mapping.FROM]:
        del request_dict[mapping.VALIDITY][mapping.FROM]

    if not request_dict[mapping.VALIDITY][mapping.TO]:
        del request_dict[mapping.VALIDITY][mapping.TO]

    await terminate_org_unit_validation(uuid_str, request_dict)
    handler = await OrgUnitRequestHandler.construct(
        request_dict, mapping.RequestType.TERMINATE
    )
    return await handler.submit()


# Generate a set of test scenarios
org_unit_uuids = [
    UUID("2874e1dc-85e6-4269-823a-e1125484dfd3"),  # Has children
    UUID("fa2e23c9-860a-4c90-bcc6-2c0721869a25"),  # No children
    UUID("00000000-0000-0000-0000-000000000000"),  # Invalid
]

now = datetime.datetime.now()
tomorrow = now + datetime.timedelta(days=1)
yesterday = now - datetime.timedelta(days=1)
from_dates = [None, now.date(), tomorrow.date()]
to_dates = [None, now.date(), tomorrow.date()]
param_tests = list(product(org_unit_uuids, from_dates, to_dates))


@pytest.mark.equivalence
@pytest.mark.usefixtures("sample_structures_no_reset")
class Tests(tests.cases.AsyncLoRATestCase):
    @parameterized.expand(
        [
            (
                (404, None),
                UUID("00000000-0000-0000-0000-000000000000"),
                "2022-07-25",
                "2022-07-25",
            ),
            (
                (400, None),
                UUID("fa2e23c9-860a-4c90-bcc6-2c0721869a25"),
                None,
                None,
            ),
            (
                (200, "fa2e23c9-860a-4c90-bcc6-2c0721869a25"),
                UUID("fa2e23c9-860a-4c90-bcc6-2c0721869a25"),
                "2022-07-25",
                "2022-07-25",
            ),
            (
                (200, "fa2e23c9-860a-4c90-bcc6-2c0721869a25"),
                UUID("fa2e23c9-860a-4c90-bcc6-2c0721869a25"),
                None,
                "2022-07-25",
            ),
            (
                (400, "fa2e23c9-860a-4c90-bcc6-2c0721869a25"),
                UUID("fa2e23c9-860a-4c90-bcc6-2c0721869a25"),
                "2022-07-25",
                None,
            ),
        ]
    )
    async def test_terminate_orgunit(
        self,
        expected_result: Tuple[int, Optional[str]],
        org_unit_id: UUID,
        from_date: Optional[str],
        to_date: Optional[str],
    ):
        url = f"/service/ou/{org_unit_id}/terminate"
        validity = {"validity": {"from": from_date, "to": to_date}}

        expected_status, expected_body = expected_result

        if not expected_status or not 200 <= expected_status < 300:
            await self.assertRequestFails(url, expected_status, json=validity)
        else:
            await self.assertRequestResponse(url, expected_body, json=validity)

    @parameterized.expand(param_tests)
    async def test_terminate_orgunit_equivalence(
        self,
        orgunit_uuid: UUID,
        from_date: Optional[datetime.date],
        to_date: Optional[datetime.date],
    ):
        uuid_str = str(orgunit_uuid)

        # Run old logic
        try:
            result_expected = await terminate_orgunit(orgunit_uuid, from_date, to_date)
        except HTTPException as e:
            result_expected = e.key
        except ValidationError:
            result_expected = ErrorCodes.E_INVALID_INPUT

        # Run new logic
        result_new = None
        try:
            path = f"/service/ou/{uuid_str}/terminate"
            terminate_object = {
                mapping.VALIDITY: {
                    mapping.FROM: from_date.isoformat() if from_date else None,
                    mapping.TO: to_date.isoformat() if to_date else None,
                },
            }

            response = await self.request(path, json=terminate_object)
            response_json = json.loads(response.content)

            if not (200 <= response.status_code < 300):
                err_key = response_json.get("error_key", "")
                getattr(ErrorCodes, err_key)(
                    obj={
                        mapping.UUID: uuid_str,
                        mapping.VALIDITY: {
                            mapping.FROM: from_date.isoformat() if from_date else None,
                            mapping.TO: to_date.isoformat() if to_date else None,
                        },
                    }
                )
            else:
                result_new = json.loads(response.content)
        except HTTPException as e:
            result_new = e.key

        # Compare and assert that the old response is the same as the new response
        self.assertEqual(result_expected, result_new)
