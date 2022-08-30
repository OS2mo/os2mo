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
import typing
from itertools import product
from typing import Optional
from uuid import UUID

import pytest
from fastapi import Body
from parameterized import parameterized
from pydantic.error_wrappers import ValidationError

import tests.cases
from mora import mapping
from mora.exceptions import ErrorCodes
from mora.exceptions import HTTPException
from mora.service.detail_writing import handle_requests
from ramodels.mo.detail import DetailTermination


# Generate a set of test scenarios
addr_uuids = [
    UUID("4e337d8e-1fd2-4449-8110-e0c8a22958ed"),  # bruger_adresse
    UUID("c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0"),  # bruger_email
    UUID("cbadfa0f-ce4f-40b9-86a0-2e85d8961f5d"),  # bruger_telefon
    UUID("00000000-0000-0000-0000-000000000000"),  # Invalid
]

now = datetime.datetime.now()
tomorrow = now + datetime.timedelta(days=1)
yesterday = now - datetime.timedelta(days=1)

validities = [(None, None), (now.date(), tomorrow.date())]

from_dates = [None, now.date(), tomorrow.date()]
to_dates = [now.date(), tomorrow.date()]
param_tests = list(product(addr_uuids, from_dates, to_dates))


async def terminate_address_legacy_implementation(
    reqs: typing.Union[typing.List[DetailTermination], DetailTermination] = Body(...)
):
    # The legacy code
    if isinstance(reqs, list):
        reqs = [req.to_dict() for req in reqs]
    elif isinstance(reqs, DetailTermination):
        reqs = reqs.to_dict()

    return await handle_requests(reqs, mapping.RequestType.TERMINATE)


@pytest.mark.equivalence
@pytest.mark.usefixtures("sample_structures_no_reset")
class Tests(tests.cases.AsyncLoRATestCase):
    @parameterized.expand(param_tests)
    async def test_equivalence_addr_terminate(
        self,
        uuid: UUID,
        from_date: Optional[datetime.date],
        to_date: datetime.date,
    ):
        # Switch "from" and "to" dates if "from" is further in the future than "to".
        # To prevent our new pydantic models from giving validation errors.
        # .. and since we dont use hypothesis in this test
        if from_date and from_date > to_date:
            prev_from_date = from_date
            from_date = to_date
            to_date = prev_from_date

        # from_date, to_date = given_validity_dts
        dt = DetailTermination(
            type=mapping.ADDRESS,
            uuid=uuid,
            validity={mapping.FROM: from_date, mapping.TO: to_date},
        )

        # Run old logic
        try:
            result_expected = await terminate_address_legacy_implementation(dt)
        except HTTPException as e:
            result_expected = e.key
        except ValidationError:
            result_expected = ErrorCodes.E_INVALID_INPUT

        # Run new logic
        result_new = None
        try:
            detail_terminate_request_dict = dt.to_dict()
            response = await self.request(
                "/service/details/terminate", json=detail_terminate_request_dict
            )
            response_json = json.loads(response.content)

            if not (200 <= response.status_code < 300):
                err_key = response_json.get("error_key", "")
                getattr(ErrorCodes, err_key)(obj=detail_terminate_request_dict)
            else:
                result_new = json.loads(response.content)
        except HTTPException as e:
            result_new = e.key

        # Compare and assert that the old response is the same as the new response
        self.assertEqual(result_expected, result_new)
