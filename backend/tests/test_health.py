# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import requests_mock
from aioresponses import aioresponses
from mock import patch
from requests.exceptions import RequestException

import tests.cases
from mora import health, config
from tests import util


class OIORestHealthTests(tests.cases.TestCase):
    @util.mock()
    def test_oio_rest_returns_true_if_reachable(self, mock):
        mock.get(config.get_settings().lora_url + "site-map")

        actual = health.oio_rest()

        self.assertEqual(True, actual)

    @util.mock()
    def test_oio_rest_returns_false_if_unreachable(self, mock):
        mock.get(config.get_settings().lora_url + "site-map", status_code=404)

        actual = health.oio_rest()

        self.assertEqual(False, actual)

    @util.mock()
    def test_oio_rest_returns_false_if_request_error(self, mock):
        mock.get(config.get_settings().lora_url + "site-map", exc=RequestException)

        actual = health.oio_rest()

        self.assertEqual(False, actual)


class ConfigurationDatabaseHealthTests(tests.cases.TestCase):
    @patch("mora.health.conf_db.health_check", new=lambda: (False, ""))
    def test_configuration_database_returns_false_if_health_check_fails(self):
        actual = health.configuration_database()

        self.assertEqual(False, actual)

    @patch("mora.health.conf_db.health_check", new=lambda: (True, ""))
    def test_configuration_database_returns_false_if_health_check_succeeds(self):
        actual = health.configuration_database()

        self.assertEqual(True, actual)


class DatasetHealthTests(tests.cases.TestCase):
    @aioresponses()
    def test_dataset_returns_false_if_no_data_found(self, mock):
        mock.get(
            config.get_settings().lora_url + "organisation/organisation?"
            "virkningfra=-infinity&virkningtil=infinity&bvn=%&konsolider=True",
            payload={"results": [[]]},
        )
        actual = health.dataset()

        self.assertEqual(False, actual)

    @aioresponses()
    def test_dataset_returns_true_if_data_found(self, mock):
        mock.get(
            (
                config.get_settings().lora_url + "organisation/organisation"
                "?virkningfra=-infinity&virkningtil=infinity&bvn=%&konsolider=True"
            ),
            payload={"results": [["f668b69a-66c4-4ba8-a783-5513178e8df1"]]},
        )

        actual = health.dataset()

        self.assertEqual(True, actual)


@requests_mock.Mocker()
class DARHealthTests(tests.cases.TestCase):
    def test_dar_returns_false_if_unreachable(self, mock):
        mock.get("https://dawa.aws.dk/autocomplete", status_code=404)

        actual = health.dar()

        self.assertEqual(False, actual)

    def test_dar_returns_false_if_request_error(self, mock):
        mock.get("https://dawa.aws.dk/autocomplete", exc=RequestException)

        actual = health.dar()

        self.assertEqual(False, actual)

    def test_dar_returns_true_if_reachable(self, mock):
        mock.get("https://dawa.aws.dk/autocomplete")

        actual = health.dar()

        self.assertEqual(True, actual)
