# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import patch
from uuid import UUID

import freezegun

from mora.handler.impl import employee, org_unit
from mora.lora import Connector
from tests.cases import TestCase


def reader_to_str(reader):
    if reader is employee.EmployeeReader:
        return "employee"
    elif reader is org_unit.OrgUnitReader:
        return "org_unit"


def endpoint_test_paramters():
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

    def reader_to_params(reader):
        target = reader_to_str(reader)
        return (
            (raw_query.format(target), search_params),
            (raw_uuid_query.format(target), uuid_search_params),
        )

    return [
        (reader, _query, _search_params)
        for reader in [employee.EmployeeReader, org_unit.OrgUnitReader]
        for _query, _search_params in reader_to_params(reader)
    ]


@freezegun.freeze_time("2017-01-01", tz_offset=1)
class Reading(TestCase):
    def test_search_endpoint(self):
        """
        tests that endpoint query params is parsed properly, and
        put into the appropriate reader classes
        :return:
        """
        # parametrized test
        for endpoint, reader in [
            ("employee", employee.EmployeeReader),
            ("org_unit", org_unit.OrgUnitReader),
        ]:
            with self.subTest(endpoint_spec=endpoint):
                with patch.object(
                    reader,
                    "get",
                ) as mock:
                    mock.return_value = {"status": "ok"}
                    resp = self.assertRequest(
                        f"/api/v1/{endpoint}?validity=present&at=2017-01-01",
                        200,
                    )
                    self.assertEqual({"status": "ok"}, resp)
                    call_args = mock.call_args_list
                    assert len(call_args) == 1
                    (connector, search_params), changed_since = call_args[0]
                    assert isinstance(connector, Connector)
                    self.assertEqual(
                        search_params, dict(validity="present", at="2017-01-01")
                    )
                    self.assertEqual(changed_since, dict(changed_since=None))

    def test_search_endpoint2(
        self,
    ):
        """
        tests that endpoint query params is parsed properly, and
        put into the appropriate reader classes
        :return:
        """
        # parametrized test
        for reader, query, search_params in endpoint_test_paramters():
            with self.subTest(endpoint_spec=reader_to_str(reader)):
                with patch.object(
                    reader,
                    "get",
                ) as mock:
                    mock.return_value = {"status": "ok"}
                    resp = self.assertRequest(
                        query,
                        200,
                    )
                    self.assertEqual({"status": "ok"}, resp)
                    call_args = mock.call_args_list
                    assert len(call_args) == 1
                    (connector, search_params), changed_since = call_args[0]
                    assert isinstance(connector, Connector)
                    self.assertEqual(search_params, search_params)
                    self.assertEqual(changed_since, dict(changed_since=None))

    def test_uuid_endpoint(self):
        """
        tests that endpoint query params is parsed properly, and
        put into the appropriate reader classes
        :return:
        """
        uuid1 = "2f16d140-d743-4c9f-9e0e-361da91a06f6"
        uuid2 = "3e702dd1-4103-4116-bb2d-b150aebe807d"
        # parametrized test
        for endpoint, reader in [
            ("employee", employee.EmployeeReader),
            ("org_unit", org_unit.OrgUnitReader),
        ]:
            with self.subTest(endpoint_spec=endpoint):
                with patch.object(
                    reader,
                    "get",
                ) as mock:
                    mock.return_value = {"status": "ok"}
                    resp = self.assertRequest(
                        f"/api/v1/{endpoint}/by_uuid?validity=present&at=2017-01-01&"
                        f"uuid={uuid1}&"  # any uuid
                        f"uuid={uuid2}",  # any uuid
                        200,
                    )
                    self.assertEqual({"status": "ok"}, resp)
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
        # parametrized test
        for endpoint, reader in [
            ("employee", employee.EmployeeReader),
            ("org_unit", org_unit.OrgUnitReader),
        ]:
            with self.subTest(endpoint_spec=endpoint):
                with patch.object(
                    reader,
                    "get",
                ) as mock:
                    mock.return_value = {"status": "ok"}
                    resp = self.assertRequest(
                        f"/api/v1/{endpoint}/by_uuid?validity=present&at=2017-01-01&"
                        f"uuid={uuid1}&"  # any uuid
                        f"uuid={uuid2}",  # any uuid
                        200,
                    )
                    self.assertEqual({"status": "ok"}, resp)
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
