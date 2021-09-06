# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from copy import deepcopy
from unittest.mock import patch
from uuid import UUID

import freezegun
from hypothesis import HealthCheck
from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st
from mora.api.v1.reading_endpoints import _extract_search_params
from mora.api.v1.reading_endpoints import orgfunk_type_map
from mora.mapping import MoOrgFunk
from tests.cases import TestCase

from .util import instance2dict


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
        self.assertEqual(expected, actual)

    @freezegun.freeze_time("2017-01-01", tz_offset=1)
    def api_exposing_org_funk_endpoint_helper(self, orgfunk, return_value):
        with self.subTest(orgfunk=orgfunk):
            with patch(
                "mora.api.v1.reading_endpoints.orgfunk_endpoint",
                return_value=return_value,
            ) as mock:
                resp = self.assertRequest(
                    f"/api/v1/{orgfunk.value}?validity=present&at=2017-01-01",
                    200,
                )
                self.assertEqual(return_value, resp)
                mock.assert_called_once_with(
                    orgfunk_type=orgfunk,
                    query_args={"validity": "present", "at": "2017-01-01"},
                    changed_since=None,
                )

    @freezegun.freeze_time("2017-01-01", tz_offset=1)
    def api_exposing_org_funk_uuid_endpoint_helper(self, orgfunk, return_value):
        with self.subTest(endpoint_spec=orgfunk):
            with patch(
                "mora.api.v1.reading_endpoints.orgfunk_endpoint",
                return_value=return_value,
            ) as mock:
                resp = self.assertRequest(
                    f"/api/v1/{orgfunk.value}/by_uuid?"
                    f"validity=present&"
                    f"at=2017-01-01&"
                    f"uuid=2f16d140-d743-4c9f-9e0e-361da91a06f6&"
                    f"uuid=3e702dd1-4103-4116-bb2d-b150aebe807d",
                    200,
                )
                self.assertEqual(return_value, resp)
                mock.assert_called_once_with(
                    orgfunk_type=orgfunk,
                    query_args={
                        "validity": "present",
                        "at": "2017-01-01",
                        "uuid": [
                            UUID("2f16d140-d743-4c9f-9e0e-361da91a06f6"),
                            UUID("3e702dd1-4103-4116-bb2d-b150aebe807d"),
                        ],
                        "only_primary_uuid": None,
                    },
                )

    def construct_orgfunk_model(self, orgfunk, data):
        model = orgfunk_type_map[orgfunk]
        instance = data.draw(st.builds(model))
        return_value = instance2dict(instance)
        return return_value

    @given(st.data())
    @settings(
        max_examples=1, suppress_health_check=[HealthCheck.too_slow], deadline=None
    )
    def test_api_exposing_org_funk_endpoint(self, data):
        # parametrized test
        for orgfunk in MoOrgFunk:
            return_value = self.construct_orgfunk_model(orgfunk, data)
            self.api_exposing_org_funk_endpoint_helper(orgfunk, [return_value])

    @given(st.data())
    @settings(
        max_examples=1, suppress_health_check=[HealthCheck.too_slow], deadline=None
    )
    def test_api_exposing_org_funk_uuid_endpoint(self, data):
        # parametrized test
        for orgfunk in MoOrgFunk:
            return_value = self.construct_orgfunk_model(orgfunk, data)
            self.api_exposing_org_funk_uuid_endpoint_helper(orgfunk, [return_value])
