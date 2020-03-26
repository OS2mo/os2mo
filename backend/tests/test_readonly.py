# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import flask
from mock import patch

from mora import readonly
from tests import util


class TestReadOnly(util.TestCase):
    @readonly.check_read_only
    def decorated(self):
        return flask.jsonify()

    def undecorated(self):
        return flask.jsonify()

    @patch("mora.readonly.conf_db.get_configuration", return_value={"read_only": True})
    def test_enabled_with_decorated_endpoint_and_ui_request(self, mock):
        """Ensure that read_only when enabled and request originates from UI"""

        self.app.add_url_rule("/test_read_only", "test_read_only", self.decorated)

        r = self.client.get("/test_read_only", headers={"X-Client-Name": "OS2mo-UI"})

        self.assertEqual(400, r.status_code)
        self.assertEqual("E_READ_ONLY", r.json["error_key"])

    @patch("mora.readonly.conf_db.get_configuration", return_value={"read_only": True})
    def test_enabled_with_decorated_endpoint_and_regular_request(self, mock):
        """Ensure that not read_only when enabled, and request is non_UI"""

        self.app.add_url_rule("/test_read_only", "test_read_only", self.decorated)

        r = self.client.get("/test_read_only")

        self.assertEqual(200, r.status_code)

    @patch("mora.readonly.conf_db.get_configuration", return_value={"read_only": True})
    def test_enabled_with_undecorated_endpoint_and_ui_request(self, mock):
        """Ensure that not read_only when enabled, with UI-request, without decorator"""

        self.app.add_url_rule("/test_read_only", "test_read_only", self.undecorated)

        r = self.client.get("/test_read_only", headers={"X-Client-Name": "OS2mo-UI"})

        self.assertEqual(200, r.status_code)

    @patch("mora.readonly.conf_db.get_configuration", return_value={"read_only": True})
    def test_enabled_with_undecorated_endpoint_and_regular_request(self, mock):
        """Ensure that not read_only when enabled, with UI-request, without decorator"""

        self.app.add_url_rule("/test_read_only", "test_read_only", self.undecorated)

        r = self.client.get("/test_read_only")

        self.assertEqual(200, r.status_code)

    @patch("mora.readonly.conf_db.get_configuration", return_value={"read_only": False})
    def test_disabled_with_decorated_endpoint_and_ui_request(self, mock):
        """Ensure that not read_only when disabled and request originates from UI"""

        self.app.add_url_rule("/test_read_only", "test_read_only", self.decorated)

        r = self.client.get("/test_read_only", headers={"X-Client-Name": "OS2mo-UI"})

        self.assertEqual(200, r.status_code)

    @patch("mora.readonly.conf_db.get_configuration", return_value={"read_only": False})
    def test_disabled_with_decorated_endpoint_and_regular_request(self, mock):
        """Ensure that not read_only when disabled, and request is non_UI"""

        self.app.add_url_rule("/test_read_only", "test_read_only", self.decorated)

        r = self.client.get("/test_read_only")

        self.assertEqual(200, r.status_code)

    @patch("mora.readonly.conf_db.get_configuration", return_value={"read_only": False})
    def test_disabled_with_undecorated_endpoint_and_ui_request(self, mock):
        """Ensure that not read_only when disabled, with UI-request, without decorator
        """

        self.app.add_url_rule("/test_read_only", "test_read_only", self.undecorated)

        r = self.client.get("/test_read_only", headers={"X-Client-Name": "OS2mo-UI"})

        self.assertEqual(200, r.status_code)

    @patch("mora.readonly.conf_db.get_configuration", return_value={"read_only": False})
    def test_disabled_with_undecorated_endpoint_and_regular_request(self, mock):
        """Ensure that not read_only when disabled, with UI-request, without decorator
        """

        self.app.add_url_rule("/test_read_only", "test_read_only", self.undecorated)

        r = self.client.get("/test_read_only")

        self.assertEqual(200, r.status_code)
