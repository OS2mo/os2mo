#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from unittest import TestCase
from mora.service.configuration_options import (
    check_config as checker)


class NoApp:
    def __init__(self):
        self.config = {}


class Tests(TestCase):

    def test_check_config_unconfigured(self):
        app = NoApp()
        with self.assertLogs('mo_configuration', level='ERROR') as log:
            with self.assertRaises(Exception):
                checker(app)
            self.assertEqual([
                'ERROR:mo_configuration:Configuration error '
                'of user settings connection information',
                'ERROR:mo_configuration:CONF_DB_USER: None',
                'ERROR:mo_configuration:CONF_DB_NAME: None',
                'ERROR:mo_configuration:CONF_DB_HOST: None',
                'ERROR:mo_configuration:CONF_DB_PORT: None',
                'ERROR:mo_configuration:Length of CONF_DB_PASSWORD: 0',
            ], log.output)

    def test_check_badly_unconfigured(self):
        app = NoApp()
        with self.assertLogs('mo_configuration', level='ERROR') as log:
            app.config.update({k: "x y z" for k in [
                "CONF_DB_USER", "CONF_DB_NAME", "CONF_DB_HOST",
                "CONF_DB_PORT", "CONF_DB_PASSWORD"
            ]})
            with self.assertRaises(Exception):
                checker(app)
            self.assertEqual([
                'ERROR:mo_configuration:Configuration database '
                'connection error',
                'ERROR:mo_configuration:Configuration database '
                'could not be opened'
            ], log.output)
