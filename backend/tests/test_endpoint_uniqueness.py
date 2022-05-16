# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import unittest

import mora.main


class TestEndpointUniqueness(unittest.TestCase):
    def test_ensure_endpoint_function_names_are_unique(self):
        non_unique_endpoints = {"index", "get_keycloak_config"}
        endpoint_func_names = [
            route.name
            for route in mora.main.app.routes
            if route.name not in non_unique_endpoints
        ]
        self.assertCountEqual(endpoint_func_names, set(endpoint_func_names))
