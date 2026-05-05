# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from unittest.mock import patch

import freezegun
import pytest
from oio_rest.oio_base import ConfiguredDBInterface
from oio_rest.oio_base import DefaultSearcher
from oio_rest.oio_base import QuickSearcher

from tests.oio_rest.util import DBTestCase


@freezegun.freeze_time("2018-01-01")
class TestCreateObject(DBTestCase):
    @pytest.fixture(autouse=True)
    def setup_objects(self):
        self.standard_virkning1 = {
            "from": "2000-01-01 12:00:00+01",
            "from_included": True,
            "to": "2020-01-01 12:00:00+01",
            "to_included": False,
        }
        self.standard_virkning2 = {
            "from": "2020-01-01 12:00:00+01",
            "from_included": True,
            "to": "2030-01-01 12:00:00+01",
            "to_included": False,
        }
        self.reference = {
            "uuid": "00000000-0000-0000-0000-000000000000",
            "virkning": self.standard_virkning1,
        }

    def parametrized_basic_integration(
        self, path: str, lora_object: dict[str, Any], search_params: dict[str, Any]
    ):
        """
        Tests basic create-search-delete-search flow
        :param path: url-style specification, e.g.: /organisation/bruger
        :param lora_object: a creatable payload consistent of the chosen path
        :param search_params: parameters that allows searching the created object
        :return:
        """

        r = self.perform_request(path, json=lora_object)

        # Check response
        self.assert201(r)

        # Check persisted data
        lora_object["livscykluskode"] = "Opstaaet"
        uuid = r.json()["uuid"]
        self.assertQueryResponse(path, lora_object, uuid=uuid)

        # test searching for objects
        # configured_db_interface.searcher = DefaultSearcher()
        with patch.object(ConfiguredDBInterface, "searcher", DefaultSearcher()):
            self.assertQueryResponse(path, [uuid], uuid=uuid, **search_params)

        # test equivalence
        # configured_db_interface.searcher = QuickSearcher()
        with patch.object(ConfiguredDBInterface, "searcher", QuickSearcher()):
            self.assertQueryResponse(path, [uuid], uuid=uuid, **search_params)

        # test delete
        deleted_uuid = self.delete(f"{path}/{uuid}", json={})
        assert uuid == deleted_uuid

        # test searching for deleted objects
        # configured_db_interface.searcher = DefaultSearcher()
        with patch.object(ConfiguredDBInterface, "searcher", DefaultSearcher()):
            self.assertQueryResponse(path, [], uuid=uuid, **search_params)

        # test equivalence
        # configured_db_interface.searcher = QuickSearcher()
        with patch.object(ConfiguredDBInterface, "searcher", QuickSearcher()):
            self.assertQueryResponse(path, [], uuid=uuid, **search_params)
