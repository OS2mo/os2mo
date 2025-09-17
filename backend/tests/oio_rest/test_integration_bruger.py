# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from tests.oio_rest.test_integration_helper import TestCreateObject


class TestCreateBruger(TestCreateObject):
    def test_bruger(self) -> None:
        # test create
        facet = {
            "attributter": {
                "brugeregenskaber": [
                    {
                        "brugervendtnoegle": "bvn",
                        "virkning": self.standard_virkning1,
                    }
                ]
            },
            "tilstande": {
                "brugergyldighed": [
                    {"gyldighed": "Aktiv", "virkning": self.standard_virkning1}
                ]
            },
        }

        path = "/organisation/bruger"
        search_params = dict(brugervendtnoegle="bvn")

        self.parametrized_basic_integration(
            path=path, lora_object=facet, search_params=search_params
        )
