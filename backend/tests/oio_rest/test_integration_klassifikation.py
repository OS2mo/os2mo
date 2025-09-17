# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from tests.oio_rest.test_integration_helper import TestCreateObject


class TestCreateKlassifikation(TestCreateObject):
    def test_create_klassifikation(self) -> None:
        klassifikation = {
            "attributter": {
                "klassifikationegenskaber": [
                    {
                        "brugervendtnoegle": "bvn",
                        "virkning": self.standard_virkning1,
                    }
                ]
            },
            "tilstande": {
                "klassifikationpubliceret": [
                    {"publiceret": "Publiceret", "virkning": self.standard_virkning1}
                ]
            },
        }

        path = "/klassifikation/klassifikation"
        search_params = dict(brugervendtnoegle="bvn")
        self.parametrized_basic_integration(
            path=path, lora_object=klassifikation, search_params=search_params
        )
