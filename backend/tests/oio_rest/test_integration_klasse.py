# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from tests.oio_rest.test_integration_helper import TestCreateObject


class TestCreateKlasse(TestCreateObject):
    def test_create_klasse(self) -> None:
        klasse = {
            "attributter": {
                "klasseegenskaber": [
                    {
                        "brugervendtnoegle": "bvn",
                        "titel": "stor titel",
                        "virkning": self.standard_virkning1,
                    }
                ]
            },
            "tilstande": {
                "klassepubliceret": [
                    {"publiceret": "Publiceret", "virkning": self.standard_virkning1}
                ]
            },
        }

        path = "/klassifikation/klasse"
        search_params = dict(brugervendtnoegle="bvn")
        self.parametrized_basic_integration(
            path=path, lora_object=klasse, search_params=search_params
        )
