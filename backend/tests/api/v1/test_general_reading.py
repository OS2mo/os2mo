# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import patch
from uuid import UUID
from typing import Dict

import freezegun
from hypothesis import given, assume, settings, strategies as st
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from mora.handler.impl import employee, org_unit
from mora.lora import Connector
from mora.api.v1.models import OrganisationUnitFull
from mora.api.v1.models import Employee
from tests.cases import TestCase
from tests.hypothesis_utils import validity_strat


def instance2dict(instance: BaseModel) -> Dict:
    """Convert a pydantic model to a jsonable dictionary.

    Args:
        instance: Instance to be converted.

    Returns:
        Dictionary which could be converted to json using json.dumps
    """
    return jsonable_encoder(instance.dict(by_alias=True))


def reader_to_str(reader):
    if reader is employee.EmployeeReader:
        return "employee"
    elif reader is org_unit.OrgUnitReader:
        return "org_unit"


def endpoint_test_parameters(reader):
    uuid1 = "2f16d140-d743-4c9f-9e0e-361da91a06f6"
    uuid2 = "3e702dd1-4103-4116-bb2d-b150aebe807d"

    raw_query = "/api/v1/{}?validity=present&at=2017-01-01"
    raw_uuid_query = (
        "/api/v1/{}/by_uuid?validity=present&at=2017-01-01&"
        f"uuid={uuid1}&"  # any uuid
        f"uuid={uuid2}"
    )  # any uuid
    search_params = dict(validity="present", at="2017-01-01")

    uuid_search_params = dict(
        validity="present",
        at="2017-01-01",
        uuid=[UUID(uuid1), UUID(uuid2)],
    )

    target = reader_to_str(reader)
    return (
        (raw_query.format(target), search_params),
        (raw_uuid_query.format(target), uuid_search_params),
    )


class Reading(TestCase):

    @freezegun.freeze_time("2017-01-01", tz_offset=1)
    def search_endpoint_helper(self, endpoint, reader, return_value):
        """
        tests that endpoint query params is parsed properly, and
        put into the appropriate reader classes
        :return:
        """
        with patch.object(
            reader,
            "get",
        ) as mock:
            mock.return_value = return_value
            resp = self.assertRequest(
                f"/api/v1/{endpoint}?validity=present&at=2017-01-01",
                200,
            )
            self.assertEqual(return_value, resp)
            call_args = mock.call_args_list
            assert len(call_args) == 1
            (connector, search_params), changed_since = call_args[0]
            assert isinstance(connector, Connector)
            self.assertEqual(
                search_params, dict(validity="present", at="2017-01-01")
            )
            self.assertEqual(changed_since, dict(changed_since=None))

    @given(st.builds(Employee))
    @settings(max_examples=1)
    def test_search_endpoint_employee(self, instance):
        self.search_endpoint_helper(
            "employee", employee.EmployeeReader, [instance2dict(instance)]
        )

    @given(st.builds(OrganisationUnitFull))
    @settings(max_examples=1)
    def test_search_endpoint_org_unit(self, instance):
        self.search_endpoint_helper(
            "org_unit", org_unit.OrgUnitReader, [instance2dict(instance)]
        )

    @freezegun.freeze_time("2017-01-01", tz_offset=1)
    def search_endpoint_helper2(self, reader, query, search_params, return_value):
        """
        tests that endpoint query params is parsed properly, and
        put into the appropriate reader classes
        :return:
        """
        with patch.object(
            reader,
            "get",
        ) as mock:
            mock.return_value = return_value
            resp = self.assertRequest(
                query,
                200,
            )
            self.assertEqual(return_value, resp)
            call_args = mock.call_args_list
            assert len(call_args) == 1
            (connector, search_params), changed_since = call_args[0]
            assert isinstance(connector, Connector)
            self.assertEqual(
                search_params, search_params
            )
            self.assertEqual(changed_since, dict(changed_since=None))

    @given(st.builds(Employee, validity=validity_strat()))
    @settings(max_examples=1)
    def test_search_endpoint_employee2(self, instance):
        assume(instance.validity.to_date)
        assume(instance.validity.from_date < instance.validity.to_date)

        reader = employee.EmployeeReader
        search_tuple, uuid_tuple = endpoint_test_parameters(reader)
        self.search_endpoint_helper2(
            reader, *search_tuple, [instance2dict(instance)]
        )
        self.search_endpoint_helper2(
            reader, *uuid_tuple, instance2dict(instance)
        )

    @given(st.builds(OrganisationUnitFull, validity=validity_strat()))
    @settings(max_examples=1)
    def test_search_endpoint_org_unit2(self, instance):
        assume(instance.validity.to_date)
        assume(instance.validity.from_date < instance.validity.to_date)

        reader = org_unit.OrgUnitReader
        search_tuple, uuid_tuple = endpoint_test_parameters(reader)
        self.search_endpoint_helper2(
            reader, *search_tuple, [instance2dict(instance)]
        )
        self.search_endpoint_helper2(
            reader, *uuid_tuple, instance2dict(instance)
        )

    @given(st.builds(Employee))
    @settings(max_examples=1)
    def test_uuid_endpoint_employee(self, instance):
        self.uuid_endpoint_helper(
            "employee", employee.EmployeeReader, instance2dict(instance)
        )

    @given(st.builds(OrganisationUnitFull))
    @settings(max_examples=1)
    def test_uuid_endpoint_org_unit(self, instance):
        self.uuid_endpoint_helper(
            "org_unit", org_unit.OrgUnitReader, instance2dict(instance)
        )

    @freezegun.freeze_time("2017-01-01", tz_offset=1)
    def uuid_endpoint_helper(self, endpoint, reader, return_value):
        """
        tests that endpoint query params is parsed properly, and
        put into the appropriate reader classes
        :return:
        """
        uuid1 = "2f16d140-d743-4c9f-9e0e-361da91a06f6"
        uuid2 = "3e702dd1-4103-4116-bb2d-b150aebe807d"
        with patch.object(
            reader,
            "get",
        ) as mock:
            mock.return_value = return_value
            resp = self.assertRequest(
                f"/api/v1/{endpoint}/by_uuid?validity=present&at=2017-01-01&"
                f"uuid={uuid1}&"  # any uuid
                f"uuid={uuid2}",  # any uuid
                200,
            )
            self.assertEqual(return_value, resp)
            call_args = mock.call_args_list
            assert len(call_args) == 1
            (connector, search_params), changed_since = call_args[0]
            assert isinstance(connector, Connector)
            self.assertEqual(
                search_params,
                dict(
                    validity="present",
                    at="2017-01-01",
                    uuid=[UUID(uuid1), UUID(uuid2)],
                ),
            )
            self.assertEqual(changed_since, dict(changed_since=None))

        uuid1 = "2f16d140-d743-4c9f-9e0e-361da91a06f6"
        uuid2 = "3e702dd1-4103-4116-bb2d-b150aebe807d"
        with patch.object(
            reader,
            "get",
        ) as mock:
            mock.return_value = return_value
            resp = self.assertRequest(
                f"/api/v1/{endpoint}/by_uuid?validity=present&at=2017-01-01&"
                f"uuid={uuid1}&"  # any uuid
                f"uuid={uuid2}",  # any uuid
                200,
            )
            self.assertEqual(return_value, resp)
            call_args = mock.call_args_list
            assert len(call_args) == 1
            (connector, search_params), changed_since = call_args[0]
            assert isinstance(connector, Connector)
            self.assertEqual(
                search_params,
                dict(
                    validity="present",
                    at="2017-01-01",
                    uuid=[UUID(uuid1), UUID(uuid2)],
                ),
            )
            self.assertEqual(changed_since, dict(changed_since=None))
