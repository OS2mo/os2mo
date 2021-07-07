# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from copy import deepcopy

from unittest.mock import patch

import freezegun

from mora.api.v1.read_orgfunk import _extract_search_params
from mora.mapping import MoOrgFunk
from tests.cases import TestCase


@freezegun.freeze_time("2017-01-01", tz_offset=1)
class Reading(TestCase):
    def test_extract_search_params(self):
        base = {"abc": "def", 123: 456}
        expected = deepcopy(base)
        expected.update(
            {
                f"tilknyttedefunktioner:{orgfunk.value}": f"some_val_{orgfunk.value}"
                for orgfunk in MoOrgFunk
            }
        )
        base.update(
            {orgfunk.value: f"some_val_{orgfunk.value}" for orgfunk in MoOrgFunk}
        )
        actual = _extract_search_params(base)
        self.assertEqual(base, base)  # non-modifying
        self.assertEqual(expected, actual)

    def test_api_exposing_org_funk_endpoint(self):
        # parametrized test
        for orgfunk in MoOrgFunk:
            with self.subTest(orgfunk=orgfunk):
                with patch(
                    "mora.api.v1.read_orgfunk.orgfunk_endpoint",
                    return_value={"status": "ok"},
                ) as mock:
                    resp = self.assertRequest(
                        f"/api/v1/{orgfunk.value}?validity=present&at=2017-01-01",
                        200,
                    )
                    self.assertEqual({"status": "ok"}, resp)
                    mock.assert_called_once_with(
                        orgfunk_type=orgfunk,
                        query_args={"validity": "present", "at": "2017-01-01"},
                    )

    def test_api_exposing_org_funk_uuid_endpoint(self):
        # parametrized test
        for orgfunk in MoOrgFunk:
            with self.subTest(orgfunk=orgfunk):
                with patch(
                    "mora.api.v1.read_orgfunk.orgfunk_endpoint",
                    return_value={"status": "ok"},
                ) as mock:
                    resp = self.assertRequest(
                        f"/api/v1/{orgfunk.value}/by_uuid?"
                        f"validity=present&"
                        f"at=2017-01-01&"
                        f"uuid=2f16d140-d743-4c9f-9e0e-361da91a06f6&"
                        f"uuid=3e702dd1-4103-4116-bb2d-b150aebe807d",
                        200,
                    )
                    self.assertEqual({"status": "ok"}, resp)
                    mock.assert_called_once_with(
                        orgfunk_type=orgfunk,
                        query_args={
                            "validity": "present",
                            "at": "2017-01-01",
                            "uuid": [
                                "2f16d140-d743-4c9f-9e0e-361da91a06f6",
                                "3e702dd1-4103-4116-bb2d-b150aebe807d",
                            ],
                        }
                    )
