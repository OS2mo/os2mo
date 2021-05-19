from unittest.mock import patch
from uuid import UUID

import freezegun
from mora.handler.impl import employee, org_unit
from mora.lora import Connector
from tests.cases import TestCase


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
