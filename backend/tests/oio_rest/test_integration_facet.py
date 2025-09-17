# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from tests.oio_rest.test_integration_helper import TestCreateObject


class TestCreateFacet(TestCreateObject):
    def test_create_facet(self) -> None:
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
