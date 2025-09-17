# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from tests.oio_rest.test_integration_helper import TestCreateObject


class TestCreateItsystem(TestCreateObject):
    def test_create_itsystem(self) -> None:
        # Create itsystem

        itsystem = {
            "note": "Nyt IT-system",
            "attributter": {
                "itsystemegenskaber": [
                    {
                        "brugervendtnoegle": "OIO_REST",
                        "itsystemnavn": "OIOXML REST API",
                        "itsystemtype": "Kommunalt system",
                        "konfigurationreference": ["Ja", "Nej", "Ved ikke"],
                        "virkning": self.standard_virkning1,
                    }
                ]
            },
            "tilstande": {
                "itsystemgyldighed": [
                    {"gyldighed": "Aktiv", "virkning": self.standard_virkning1}
                ]
            },
        }

        path = "/organisation/itsystem"
        search_params = dict(
            brugervendtnoegle="OIO_REST", itsystemnavn="OIOXML REST API"
        )
        self.parametrized_basic_integration(
            path=path, lora_object=itsystem, search_params=search_params
        )
