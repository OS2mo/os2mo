import datetime
from itertools import product
from typing import Optional
from typing import Tuple
from uuid import UUID

import pytest
from parameterized import parameterized

import tests.cases

org_unit_uuids = [
    UUID("2874e1dc-85e6-4269-823a-e1125484dfd3"),
    UUID("00000000-0000-0000-0000-000000000000"),
]

# now = datetime.datetime.now()
#
# from_dates = [None, now.date().isoformat()]
# to_dates = [None, now.date().isoformat()]
#
#
# param_tests = list(
#     product(org_unit_uuids, from_dates, to_dates)
# )


# async def terminate_orgunit(
#     orgunit_id: UUID,
#     from_date: Optional[str],
#     to_date: Optional[str]
# ):
#     pass


@pytest.mark.equivalence
@pytest.mark.usefixtures("sample_structures_no_reset")
class Tests(tests.cases.AsyncLoRATestCase):

    # @parameterized.expand(param_tests)
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
    async def test_terminate_orgunit_equivalence(
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
