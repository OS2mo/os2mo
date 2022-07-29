# SPDX-FileCopyrightText: 2017-2021 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import tests.cases
from mora.handler.reading import OrgFunkReadingHandler
from mora.lora import Connector
from tests.util import sample_structures_minimal_cls_fixture


@sample_structures_minimal_cls_fixture
class TestOrgFunkReadingHandler(tests.cases.AsyncLoRATestCase):
    def setUp(self):
        super().setUp()
        self._unitid = "2874e1dc-85e6-4269-823a-e1125484dfd3"
        self._connector = Connector(virkningfra="-infinity", virkningtil="infinity")
        self._args = self._connector, "ou", self._unitid

    async def test_get_search_fields(self):
        result = OrgFunkReadingHandler._get_search_fields("ou", self._unitid)
        self.assertDictEqual(
            result,
            {OrgFunkReadingHandler.SEARCH_FIELDS["ou"]: self._unitid},
        )

    async def test_get_from_type(self):
        result = await OrgFunkReadingHandler.get_from_type(*self._args)
        self.assertIsInstance(result, list)
        self.assertSetEqual(
            set(item["user_key"] for item in result),
            set(["rod <-> fil", "rod <-> hum"]),
        )

    async def test_get_count(self):
        # This counts the 2 org funcs of type "tilknyttedeenheder"
        # ("rod <-> fil", "rod <-> hum")
        result = await OrgFunkReadingHandler.get_count(*self._args)
        self.assertEqual(result, 2)
