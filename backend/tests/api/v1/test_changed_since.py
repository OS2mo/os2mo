# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from backend.mora.async_util import async_to_sync
from datetime import datetime
from urllib import parse

import freezegun

from mora.mapping import MoOrgFunk
from mora.util import DEFAULT_TIMEZONE
from tests.cases import ConfigTestCase


def changed_since_parameters():
    changed_since_future = datetime(9999, 1, 1)
    changed_since_past = datetime(1930, 1, 1)
    return (
        [(funk.value, changed_since_future, False) for funk in MoOrgFunk]
        + [(funk.value, changed_since_past, True) for funk in MoOrgFunk]
        + [
            ("employee", changed_since_future, False),
            ("employee", changed_since_past, True),
            ("org_unit", changed_since_future, False),
            ("org_unit", changed_since_past, True),
        ]
    )


@freezegun.freeze_time("2017-01-01", tz_offset=1)
class ChangedSinceBasic(ConfigTestCase):
    def test_changed_since(self):
        """
        tests that the "changed_since" parameter does anything
        :return:
        """
        self.load_sample_structures(minimal=False)

        for endpoint, changed_since, any_results in changed_since_parameters():
            with self.subTest(endpoint=endpoint):
                resp = self.assertRequest(
                    f"/api/v1/{endpoint}?changed_since={str(changed_since)}",
                    200,
                )
                self.assertEqual(any_results, bool(resp))


class ChangedSinceEmployee(ConfigTestCase):
    def _req_endpoint(self, endpoint: str, changed_since: datetime, expected: bool):
        resp = self.assertRequest(
            f"/api/v1/{endpoint}?changed_since={parse.quote(str(changed_since))}",
            200,
        )
        # Nothing changed since "now"
        self.assertEqual(expected, bool(resp))

    def __edit_employee(self):
        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"
        req = [
            {
                "type": "employee",
                "original": None,
                "data": {
                    "validity": {
                        "from": "2017-02-02",
                    },
                    "user_key": "regnbøfssalat",
                    "cpr_no": "0101010101",
                    "givenname": "Martin L",
                    "surname": "Gore",
                    "nickname_givenname": "John",
                    "nickname_surname": "Morfar",
                    "seniority": "2017-01-01",
                },
                "uuid": userid,
            }
        ]
        self.assertRequestResponse(
            "/service/details/edit",
            [userid],
            json=req,
            amqp_topics={"employee.employee.update": 1},
        )

    @async_to_sync
    async def test_changed_since_with_edit(self):
        """
        tests changed_since actually filters the expected
        :return:
        """
        await self.aload_sample_structures(minimal=False)
        changed_since = datetime.now(tz=DEFAULT_TIMEZONE)
        endpoint = "employee"
        # test once
        self._req_endpoint(endpoint, changed_since, False)
        self.__edit_employee()
        # test again
        self._req_endpoint(endpoint, changed_since, True)
