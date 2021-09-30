# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import datetime

import freezegun
import pytest
from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st

from mora import util
from mora.api.v1.models import Employee
from mora.api.v1.models import OrganisationUnitFull
from mora.api.v1.models import RelatedUnit
from mora.handler import reading
from mora.handler.impl import employee
from mora.handler.impl import org_unit

from . import base
from .util import instance2dict


class ReadingWithAtTestCase(base.BaseReadingTestCase):
    @given(st.builds(Employee))
    @settings(max_examples=1)
    def test_search_employee_with_validity(self, instance):
        mock = self.search_endpoint_helper(
            employee.EmployeeReader,
            [instance2dict(instance)],
            parameters={
                "validity": "future",
            },
        )
        self.assertEqual(mock.connector.end, util.POSITIVE_INFINITY)

    @given(st.builds(OrganisationUnitFull))
    @settings(max_examples=1)
    def test_search_org_unit_with_validity(self, instance):
        mock = self.search_endpoint_helper(
            org_unit.OrgUnitReader,
            [instance2dict(instance)],
            parameters={
                "validity": "past",
            },
        )
        self.assertEqual(mock.connector.start, util.NEGATIVE_INFINITY)

    @given(st.builds(RelatedUnit))
    @settings(max_examples=1)
    def test_search_related_unit_with_validity(self, instance):
        mock = self.search_endpoint_helper(
            reading.OrgFunkReadingHandler,
            [instance2dict(instance)],
            endpoint="related_unit",
            parameters={
                "validity": "2012-03-04/2056-07-08",
            },
        )
        self.assertEqual(
            mock.connector.start,
            datetime.datetime(2012, 3, 4, tzinfo=util.DEFAULT_TIMEZONE),
        )
        self.assertEqual(
            mock.connector.end,
            datetime.datetime(2056, 7, 8, tzinfo=util.DEFAULT_TIMEZONE),
        )

    @given(st.builds(Employee))
    @settings(max_examples=1)
    def test_uuid_employee_with_validity(self, instance):
        mock = self.uuid_endpoint_helper(
            employee.EmployeeReader,
            [instance2dict(instance)],
            parameters={
                "validity": "-infinity/2056-07-08",
            },
        )
        self.assertEqual(
            mock.connector.start,
            util.NEGATIVE_INFINITY,
        )
        self.assertEqual(
            mock.connector.end,
            datetime.datetime(2056, 7, 8, tzinfo=util.DEFAULT_TIMEZONE),
        )

    @given(st.builds(OrganisationUnitFull))
    @settings(max_examples=1)
    @pytest.mark.xfail
    def test_uuid_org_unit_with_validity(self, instance):
        mock = self.uuid_endpoint_helper(
            org_unit.OrgUnitReader,
            [instance2dict(instance)],
            parameters={
                "validity": "-infinity/infinity",
            },
        )
        self.assertEqual(mock.connector.start, util.NEGATIVE_INFINITY)
        self.assertEqual(mock.connector.end, util.POSITIVE_INFINITY)

    @given(st.builds(RelatedUnit))
    @settings(max_examples=1)
    def test_uuid_related_unit_with_validity(self, instance):
        with freezegun.freeze_time("2017-01-01", tz_offset=1):
            mock = self.uuid_endpoint_helper(
                reading.OrgFunkReadingHandler,
                [instance2dict(instance)],
                endpoint="related_unit/by_uuid",
                parameters={
                    "validity": "present",
                },
            )
            self.assertEqual(mock.connector.start, util.now())
            self.assertEqual(mock.connector.end, util.now() + util.MINIMAL_INTERVAL)
