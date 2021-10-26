# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st
from mora.api.v1.models import Address
from mora.api.v1.models import Employee
from mora.api.v1.models import OrganisationUnitFull
from mora.api.v1.models import RelatedUnit
from mora.handler import reading
from mora.handler.impl import employee
from mora.handler.impl import org_unit

from . import base
from .util import instance2dict


class GeneralReadingTestCase(base.BaseReadingTestCase):

    app_settings_overrides = {"v1_api_enable": True}

    @given(st.builds(Employee))
    @settings(max_examples=1)
    def test_search_endpoint_employee(self, instance):
        self.search_endpoint_helper(employee.EmployeeReader, [instance2dict(instance)])

    @given(st.builds(OrganisationUnitFull))
    @settings(max_examples=1)
    def test_search_endpoint_org_unit(self, instance):
        self.search_endpoint_helper(org_unit.OrgUnitReader, [instance2dict(instance)])

    @given(st.builds(RelatedUnit))
    @settings(max_examples=1)
    def test_search_endpoint_related_unit(self, instance):
        """
        All endpoints except employee and org_unit uses the organisation function
        reading handler, so it should be sufficient to test any one of them.
        """
        self.search_endpoint_helper(
            reading.OrgFunkReadingHandler,
            [instance2dict(instance)],
            endpoint="related_unit",
        )

    @given(st.builds(Employee))
    @settings(max_examples=1)
    def test_uuid_endpoint_employee(self, instance):
        self.uuid_endpoint_helper(employee.EmployeeReader, [instance2dict(instance)])

    @given(st.builds(OrganisationUnitFull))
    @settings(max_examples=1)
    def test_uuid_endpoint_org_unit(self, instance):
        self.uuid_endpoint_helper(org_unit.OrgUnitReader, [instance2dict(instance)])

    @given(st.builds(Address))
    @settings(max_examples=1)
    def test_uuid_endpoint_address(self, instance):
        self.uuid_endpoint_helper(
            reading.OrgFunkReadingHandler,
            [instance2dict(instance)],
            endpoint="address/by_uuid",
        )
