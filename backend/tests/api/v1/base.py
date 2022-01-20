# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import urllib.parse
from unittest.mock import patch
from uuid import UUID

import freezegun
from mora.lora import Connector
from tests.cases import TestCase

from backend.tests.api.v1.util import reader_to_endpoint


class BaseReadingTestCase(TestCase):
    @freezegun.freeze_time("2017-01-01", tz_offset=1)
    def search_endpoint_helper(self, reader, return_value, endpoint=None, parameters=None):
        """
        tests that endpoint query params is parsed properly, and
        put into the appropriate reader classes
        """
        if endpoint is None:
            endpoint = reader_to_endpoint(reader)
        if parameters is None:
            parameters = {}
        with patch.object(reader, "get") as mock:
            mock.return_value = return_value
            resp = self.assertRequest(
                "/api/v1/{endpoint}?{parameters}".format(
                    endpoint=endpoint,
                    parameters=urllib.parse.urlencode(parameters, doseq=True),
                ),
                200,
            )
            self.assertEqual(return_value, resp)
            self.assertEqual(mock.call_count, 1)
            try:
                mock.connector = mock.call_args.args[0]
            except IndexError:
                mock.connector = mock.call_args.kwargs["c"]
            self.assertIsInstance(mock.connector, Connector)
            try:
                mock.search_fields = mock.call_args.args[1]
            except IndexError:
                mock.search_fields = mock.call_args.kwargs["search_fields"]
            self.assertNotIn("at", mock.search_fields)
            self.assertNotIn("validity", mock.search_fields)
            self.assertNotIn("changed_since", mock.search_fields)
            return mock

    def uuid_endpoint_helper(self, reader, return_value, endpoint=None, parameters=None):
        uuid1 = "2f16d140-d743-4c9f-9e0e-361da91a06f6"
        uuid2 = "3e702dd1-4103-4116-bb2d-b150aebe807d"
        if endpoint is None:
            endpoint = f"{reader_to_endpoint(reader)}/by_uuid"
        if parameters is None:
            parameters = {}
        mock = self.search_endpoint_helper(
            reader=reader,
            return_value=return_value,
            endpoint=endpoint,
            parameters=dict(uuid=[UUID(uuid1), UUID(uuid2)], **parameters),
        )
        self.assertDictContainsSubset(
            dict(
                uuid=[UUID(uuid1), UUID(uuid2)],
            ),
            mock.search_fields,
        )
        return mock
