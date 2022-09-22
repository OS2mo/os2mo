# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from tests.oio_rest.test_integration_helper import TestCreateObject


class TestCreateFacet(TestCreateObject):
    def setUp(self):
        super().setUp()

    def test_create_facet(self):
        facet = {
            "attributter": {
                "facetegenskaber": [
                    {
                        "brugervendtnoegle": "bvn",
                        "virkning": self.standard_virkning1,
                    }
                ]
            },
            "tilstande": {
                "facetpubliceret": [
                    {"publiceret": "Publiceret", "virkning": self.standard_virkning1}
                ]
            },
        }

        path = "/klassifikation/facet"
        search_params = dict(brugervendtnoegle="bvn")
        self.parametrized_basic_integration(
            path=path, lora_object=facet, search_params=search_params
        )
