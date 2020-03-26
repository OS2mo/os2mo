# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import requests_mock
from mock import patch
from requests.exceptions import RequestException

from tests import util

from mora import health
from mora.settings import config


class OIORestHealthTests(util.TestCase):
    @util.mock()
    def test_oio_rest_returns_true_if_reachable(self, mock):

        mock.get(config["lora"]["url"] + "site-map")

        actual = health.oio_rest()

        self.assertEqual(True, actual)

    @util.mock()
    def test_oio_rest_returns_false_if_unreachable(self, mock):

        mock.get(config["lora"]["url"] + "site-map", status_code=404)

        actual = health.oio_rest()

        self.assertEqual(False, actual)

    @util.mock()
    def test_oio_rest_returns_false_if_request_error(self, mock):
        mock.get(config["lora"]["url"] + "site-map", exc=RequestException)

        actual = health.oio_rest()

        self.assertEqual(False, actual)


class SessionDatabaseHealthTests(util.TestCase):
    @util.override_config({"saml_sso": {"enable": False}})
    def test_session_database_returns_none_on_sso_not_enabled(self):

        actual = health.session_database()

        self.assertEqual(None, actual)

    @util.override_config({"saml_sso": {"enable": True}})
    @patch('mora.health.session_database_health', new=lambda x: True)
    def test_session_database_returns_true_if_health_check_succeeds(self):

        actual = health.session_database()

        self.assertEqual(True, actual)

    @util.override_config({"saml_sso": {"enable": True}})
    @patch('mora.health.session_database_health', new=lambda x: False)
    def test_session_database_returns_false_if_health_check_fails(self):

        actual = health.session_database()

        self.assertEqual(False, actual)


class ConfigurationDatabaseHealthTests(util.TestCase):
    @patch("mora.health.conf_db.health_check", new=lambda: (False, ""))
    def test_configuration_database_returns_false_if_health_check_fails(self):

        actual = health.configuration_database()

        self.assertEqual(False, actual)

    @patch("mora.health.conf_db.health_check", new=lambda: (True, ""))
    def test_configuration_database_returns_false_if_health_check_succeeds(self):

        actual = health.configuration_database()

        self.assertEqual(True, actual)


@requests_mock.Mocker()
class DatasetHealthTests(util.TestCase):
    def test_dataset_returns_false_if_no_data_found(self, mock):
        mock.get(
            (
                config["lora"]["url"] + "organisation/organisation"
                "?virkningfra=-infinity&virkningtil=infinity&bvn=%"
            ),
            text='{"results":[[]]}',
        )

        actual = health.dataset()

        self.assertEqual(False, actual)

    def test_dataset_returns_true_if_data_found(self, mock):
        mock.get(
            (
                config["lora"]["url"] + "organisation/organisation"
                "?virkningfra=-infinity&virkningtil=infinity&bvn=%"
            ),
            text='{"results":[["f668b69a-66c4-4ba8-a783-5513178e8df1"]]}',
        )

        actual = health.dataset()

        self.assertEqual(True, actual)


@requests_mock.Mocker()
class DARHealthTests(util.TestCase):
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


@requests_mock.Mocker()
class IdPHealthTests(util.TestCase):
    @util.override_config({"saml_sso": {"enable": False}})
    def test_idp_returns_none_if_saml_sso_not_enabled(self, rq_mock):

        actual = health.idp()

        self.assertEqual(None, actual)

    @util.override_config({"saml_sso": {"enable": True}})
    @patch('mora.health.idp_health', new=lambda x: True)
    def test_idp_returns_true_if_idp_reachable(self, rq_mock):

        actual = health.idp()

        self.assertEqual(True, actual)

    @util.override_config({"saml_sso": {"enable": True}})
    @patch('mora.health.idp_health', new=lambda x: False)
    def test_idp_returns_false_if_request_exception(self, rq_mock):

        actual = health.idp()

        self.assertEqual(False, actual)
