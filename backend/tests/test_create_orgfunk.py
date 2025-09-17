# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from mora.common import create_organisationsfunktion_payload


def test_create_organisation_full() -> None:
    output_org_funk = {
        "attributter": {
            "organisationfunktionegenskaber": [
                {
                    "funktionsnavn": "funktionsnavn",
                    "brugervendtnoegle": "brugervendtnoegle",
                    "virkning": {
                        "from": "2016-01-01T00:00:00+01:00",
                        "to": "2018-01-01T00:00:00+01:00",
                    },
                }
            ]
        },
        "note": "Oprettet i MO",
        "relationer": {
            "tilknyttedeenheder": [
                {
                    "uuid": "a30f5f68-9c0d-44e9-afc9-04e58f52dfec",
                    "virkning": {
                        "from": "2016-01-01T00:00:00+01:00",
                        "to": "2018-01-01T00:00:00+01:00",
                    },
                },
                {
                    "uuid": "3f2e320e-d265-4480-a4f6-b92e40cf91b3",
                    "virkning": {
                        "from": "2016-01-01T00:00:00+01:00",
                        "to": "2018-01-01T00:00:00+01:00",
                    },
                },
            ],
            "tilknyttedebrugere": [
                {
                    "uuid": "0b745aa2-6cf8-44a7-a7bc-9b7f75ce0ad6",
                    "virkning": {
                        "from": "2016-01-01T00:00:00+01:00",
                        "to": "2018-01-01T00:00:00+01:00",
                    },
                },
                {
                    "uuid": "c20a1d60-33df-4dd3-9509-125e66b124eb",
                    "virkning": {
                        "from": "2016-01-01T00:00:00+01:00",
                        "to": "2018-01-01T00:00:00+01:00",
                    },
                },
            ],
            "organisatoriskfunktionstype": [
                {
                    "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
                    "virkning": {
                        "from": "2016-01-01T00:00:00+01:00",
                        "to": "2018-01-01T00:00:00+01:00",
                    },
                }
            ],
            "tilknyttedeorganisationer": [
                {
                    "uuid": "f494ad89-039d-478e-91f2-a63566554bd6",
                    "virkning": {
                        "from": "2016-01-01T00:00:00+01:00",
                        "to": "2018-01-01T00:00:00+01:00",
                    },
                }
            ],
            "opgaver": [
                {
                    "uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8",
                    "virkning": {
                        "from": "2016-01-01T00:00:00+01:00",
                        "to": "2018-01-01T00:00:00+01:00",
                    },
                },
                {
                    "uuid": "8017363b-e836-41c1-8511-2287d8fbc8a2",
                    "virkning": {
                        "from": "2016-01-01T00:00:00+01:00",
                        "to": "2018-01-01T00:00:00+01:00",
                    },
                },
            ],
        },
        "tilstande": {
            "organisationfunktiongyldighed": [
                {
                    "virkning": {
                        "from": "2016-01-01T00:00:00+01:00",
                        "to": "2018-01-01T00:00:00+01:00",
                    },
                    "gyldighed": "Aktiv",
                }
            ]
        },
    }

    funktionsnavn = "funktionsnavn"
    valid_from = "2016-01-01T00:00:00+01:00"
    valid_to = "2018-01-01T00:00:00+01:00"
    brugervendtnoegle = "brugervendtnoegle"
    tilknyttedebrugere = [
        "0b745aa2-6cf8-44a7-a7bc-9b7f75ce0ad6",
        "c20a1d60-33df-4dd3-9509-125e66b124eb",
    ]
    tilknyttedeorganisationer = ["f494ad89-039d-478e-91f2-a63566554bd6"]
    tilknyttedeenheder = [
        "a30f5f68-9c0d-44e9-afc9-04e58f52dfec",
        "3f2e320e-d265-4480-a4f6-b92e40cf91b3",
    ]
    funktionstype = "62ec821f-4179-4758-bfdf-134529d186e9"
    opgaver = [
        {
            "uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8",
        },
        {"uuid": "8017363b-e836-41c1-8511-2287d8fbc8a2"},
    ]

    assert (
        create_organisationsfunktion_payload(
            funktionsnavn=funktionsnavn,
            valid_from=valid_from,
            valid_to=valid_to,
            brugervendtnoegle=brugervendtnoegle,
            tilknyttedeorganisationer=tilknyttedeorganisationer,
            tilknyttedebrugere=tilknyttedebrugere,
            tilknyttedeenheder=tilknyttedeenheder,
            funktionstype=funktionstype,
            opgaver=opgaver,
        )
        == output_org_funk
    ), "Org funktion not created correctly from FE req"


def test_create_organisationfunktion_minimal() -> None:
    output_org_funk = {
        "attributter": {
            "organisationfunktionegenskaber": [
                {
                    "funktionsnavn": "funktionsnavn",
                    "brugervendtnoegle": "brugervendtnoegle",
                    "virkning": {
                        "from": "2016-01-01T00:00:00+01:00",
                        "to": "2018-01-01T00:00:00+01:00",
                    },
                }
            ]
        },
        "note": "Oprettet i MO",
        "relationer": {
            "tilknyttedebrugere": [
                {
                    "uuid": "0b745aa2-6cf8-44a7-a7bc-9b7f75ce0ad6",
                    "virkning": {
                        "from": "2016-01-01T00:00:00+01:00",
                        "to": "2018-01-01T00:00:00+01:00",
                    },
                }
            ],
            "tilknyttedeorganisationer": [
                {
                    "uuid": "f494ad89-039d-478e-91f2-a63566554bd6",
                    "virkning": {
                        "from": "2016-01-01T00:00:00+01:00",
                        "to": "2018-01-01T00:00:00+01:00",
                    },
                }
            ],
        },
        "tilstande": {
            "organisationfunktiongyldighed": [
                {
                    "virkning": {
                        "from": "2016-01-01T00:00:00+01:00",
                        "to": "2018-01-01T00:00:00+01:00",
                    },
                    "gyldighed": "Aktiv",
                }
            ]
        },
    }

    funktionsnavn = "funktionsnavn"
    valid_from = "2016-01-01T00:00:00+01:00"
    valid_to = "2018-01-01T00:00:00+01:00"
    brugervendtnoegle = "brugervendtnoegle"
    tilknyttedebrugere = ["0b745aa2-6cf8-44a7-a7bc-9b7f75ce0ad6"]
    tilknyttedeorganisationer = ["f494ad89-039d-478e-91f2-a63566554bd6"]

    assert (
        create_organisationsfunktion_payload(
            funktionsnavn=funktionsnavn,
            valid_from=valid_from,
            valid_to=valid_to,
            brugervendtnoegle=brugervendtnoegle,
            tilknyttedebrugere=tilknyttedebrugere,
            tilknyttedeorganisationer=tilknyttedeorganisationer,
        )
        == output_org_funk
    ), "Org funktion not created correctly from FE req"
