# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import datetime

import pytest
import freezegun
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


@pytest.mark.skip(reason="Deprecated: Replaced by GraphQL")
class ReadingWithAtTestCase(base.BaseReadingTestCase):

    app_settings_overrides = {"v1_api_enable": True}

    @given(instance=st.builds(Employee))
    @settings(max_examples=1)
    @freezegun.freeze_time("2017-01-01", tz_offset=1)
    def test_search_employee_with_at(self, instance):
        mock = self.search_endpoint_helper(
            employee.EmployeeReader,
            [instance2dict(instance)],
            parameters={
                "at": "2012-03-04",
            },
        )
        self.assertEqual(
            mock.connector.now,
            datetime.datetime(2012, 3, 4, tzinfo=util.DEFAULT_TIMEZONE),
        )

    @given(instance=st.builds(OrganisationUnitFull))
    @settings(max_examples=1)
    @freezegun.freeze_time("2017-01-01", tz_offset=1)
    def test_search_org_unit_with_at(self, instance):
        mock = self.search_endpoint_helper(
            org_unit.OrgUnitReader,
            [instance2dict(instance)],
            parameters={
                "at": "2012-03-04T09:41:20-03:00",
            },
        )
        self.assertEqual(
            mock.connector.now,
            datetime.datetime(2012, 3, 4, 13, 41, 20, tzinfo=util.DEFAULT_TIMEZONE),
        )

    @given(instance=st.builds(RelatedUnit))
    @settings(max_examples=1)
    @freezegun.freeze_time("2017-01-01", tz_offset=1)
    def test_search_related_unit_with_at(self, instance):
        mock = self.search_endpoint_helper(
            reading.OrgFunkReadingHandler,
            [instance2dict(instance)],
            endpoint="related_unit",
            parameters={
                "at": "2012-03-04T12:37:46",
            },
        )
        self.assertEqual(
            mock.connector.now,
            datetime.datetime(2012, 3, 4, 12, 37, 46, tzinfo=util.DEFAULT_TIMEZONE),
        )

    @given(instance=st.builds(Employee))
    @settings(max_examples=1)
    @freezegun.freeze_time("2017-01-01", tz_offset=1)
    def test_uuid_employee_with_at(self, instance):
        mock = self.uuid_endpoint_helper(
            employee.EmployeeReader,
            [instance2dict(instance)],
            parameters={
                "at": "2012-03-04",
            },
        )
        self.assertEqual(
            mock.connector.now,
            datetime.datetime(2012, 3, 4, tzinfo=util.DEFAULT_TIMEZONE),
        )

    @given(instance=st.builds(OrganisationUnitFull))
    @settings(max_examples=1)
    @freezegun.freeze_time("2017-01-01", tz_offset=1)
    def test_uuid_org_unit_with_at(self, instance):
        mock = self.uuid_endpoint_helper(
            org_unit.OrgUnitReader,
            [instance2dict(instance)],
            parameters={
                "at": "20120304",
            },
        )
        self.assertEqual(
            mock.connector.now,
            datetime.datetime(2012, 3, 4, tzinfo=util.DEFAULT_TIMEZONE),
        )

    @given(instance=st.builds(RelatedUnit))
    @settings(max_examples=1)
    @freezegun.freeze_time("2017-01-01", tz_offset=1)
    def test_uuid_related_unit_with_at(self, instance):
        mock = self.uuid_endpoint_helper(
            reading.OrgFunkReadingHandler,
            [instance2dict(instance)],
            endpoint="related_unit/by_uuid",
            parameters={
                "at": "2012-03-04T07:33Z",
            },
        )
        self.assertEqual(
            mock.connector.now,
            datetime.datetime(2012, 3, 4, 8, 33, tzinfo=util.DEFAULT_TIMEZONE),
        )
