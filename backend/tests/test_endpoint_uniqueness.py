# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import unittest

import mora.main


class TestEndpointUniqueness(unittest.TestCase):

    def test_ensure_endpoint_function_names_are_unique(self):

        endpoint_func_names = [route.name for route in mora.main.app.routes]

        # The "index" endpoint function in mora.app.py is not unique, so
        # we have to account for that
        number_of_index_endpoints = endpoint_func_names.count('index')

        self.assertEqual(
            len(set(endpoint_func_names)),
            len(endpoint_func_names) - (number_of_index_endpoints - 1)
        )
