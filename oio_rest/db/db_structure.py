# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from copy import deepcopy

# This specifies the database structure
DATABASE_STRUCTURE = {
    "facet": {
        "attributter": {
            "egenskaber": [
                "brugervendtnoegle",
                "beskrivelse",
                "opbygning",
                "ophavsret",
                "plan",
                "supplement",
                "retskilde",
            ],
        },
        "attributter_metadata": {
            "egenskaber": {"brugervendtnoegle": {"mandatory": True}}
        },
        "tilstande": {"publiceret": ["Publiceret", "IkkePubliceret"]},
        "relationer_nul_til_en": ["ansvarlig", "ejer", "facettilhoerer"],
        "relationer_nul_til_mange": ["redaktoerer"],
    },
    "klassifikation": {
        "attributter": {
            "egenskaber": [
                "brugervendtnoegle",
                "beskrivelse",
                "kaldenavn",
                "ophavsret",
            ],
        },
        "attributter_metadata": {
            "egenskaber": {"brugervendtnoegle": {"mandatory": True}}
        },
        "tilstande": {"publiceret": ["Publiceret", "IkkePubliceret"]},
        "relationer_nul_til_en": ["ansvarlig", "ejer"],
        "relationer_nul_til_mange": [],
    },
    # Please notice, that the db templating code for klasse, is changed by
    # patches that are applied to handle the special case of 'soegeord' in the
    # 'egenskaber'-attribute.
    "klasse": {
        "attributter": {
            "egenskaber": [
                "brugervendtnoegle",
                "beskrivelse",
                "eksempel",
                "omfang",
                "titel",
                "retskilde",
                "aendringsnotat",
            ],
        },
        "attributter_metadata": {
            "egenskaber": {
                "brugervendtnoegle": {"mandatory": True},
                "titel": {"mandatory": True},
            }
        },
        "tilstande": {"publiceret": ["Publiceret", "IkkePubliceret"]},
        "relationer_nul_til_en": ["ejer", "ansvarlig", "overordnetklasse", "facet"],
        "relationer_nul_til_mange": [
            "redaktoerer",
            "sideordnede",
            "mapninger",
            "tilfoejelser",
            "erstatter",
            "lovligekombinationer",
        ],
    },
    "bruger": {
        "attributter": {
            "egenskaber": [
                "brugervendtnoegle",
                "brugernavn",
                "brugertype",
            ],
            "udvidelser": [
                "fornavn",
                "efternavn",
                "kaldenavn_fornavn",
                "kaldenavn_efternavn",
                "seniority",
            ],
        },
        "attributter_metadata": {
            "egenskaber": {"brugervendtnoegle": {"mandatory": True}}
        },
        "tilstande": {"gyldighed": ["Aktiv", "Inaktiv"]},
        "relationer_nul_til_en": ["tilhoerer"],
        "relationer_nul_til_mange": [
            "adresser",
            "brugertyper",
            "opgaver",
            "tilknyttedeenheder",
            "tilknyttedefunktioner",
            "tilknyttedeinteressefaellesskaber",
            "tilknyttedeorganisationer",
            "tilknyttedepersoner",
            "tilknyttedeitsystemer",
        ],
    },
    "itsystem": {
        "attributter": {
            "egenskaber": [
                "brugervendtnoegle",
                "itsystemnavn",
                "itsystemtype",
                "konfigurationreference",
            ],
        },
        "attributter_metadata": {
            "egenskaber": {
                "brugervendtnoegle": {"mandatory": True},
                "konfigurationreference": {"type": "text[]"},
            }
        },
        "tilstande": {"gyldighed": ["Aktiv", "Inaktiv"]},
        "relationer_nul_til_en": ["tilhoerer"],
        "relationer_nul_til_mange": [
            "tilknyttedeorganisationer",
            "tilknyttedeenheder",
            "tilknyttedefunktioner",
            "tilknyttedebrugere",
            "tilknyttedeinteressefaellesskaber",
            "tilknyttedeitsystemer",
            "tilknyttedepersoner",
            "systemtyper",
            "opgaver",
            "adresser",
        ],
    },
    "organisation": {
        "attributter": {
            "egenskaber": [
                "brugervendtnoegle",
                "organisationsnavn",
            ],
        },
        "attributter_metadata": {
            "egenskaber": {"brugervendtnoegle": {"mandatory": True}}
        },
        "tilstande": {"gyldighed": ["Aktiv", "Inaktiv"]},
        "relationer_nul_til_en": [
            "branche",
            "myndighed",
            "myndighedstype",
            "overordnet",
            "produktionsenhed",
            "skatteenhed",
            "tilhoerer",
            "virksomhed",
            "virksomhedstype",
        ],
        "relationer_nul_til_mange": [
            "adresser",
            "ansatte",
            "opgaver",
            "tilknyttedebrugere",
            "tilknyttedeenheder",
            "tilknyttedefunktioner",
            "tilknyttedeinteressefaellesskaber",
            "tilknyttedeorganisationer",
            "tilknyttedepersoner",
            "tilknyttedeitsystemer",
        ],
    },
    "organisationenhed": {
        "attributter": {
            "egenskaber": [
                "brugervendtnoegle",
                "enhedsnavn",
            ],
        },
        "attributter_metadata": {
            "egenskaber": {"brugervendtnoegle": {"mandatory": True}}
        },
        "tilstande": {"gyldighed": ["Aktiv", "Inaktiv"]},
        "relationer_nul_til_en": [
            "branche",
            "enhedstype",
            "overordnet",
            "produktionsenhed",
            "skatteenhed",
            "tilhoerer",
            "niveau",
        ],
        "relationer_nul_til_mange": [
            "adresser",
            "ansatte",
            "opgaver",
            "tilknyttedebrugere",
            "tilknyttedeenheder",
            "tilknyttedefunktioner",
            "tilknyttedeinteressefaellesskaber",
            "tilknyttedeorganisationer",
            "tilknyttedepersoner",
            "tilknyttedeitsystemer",
            "opmærkning",
        ],
    },
    "organisationfunktion": {
        "attributter": {
            "egenskaber": [
                "brugervendtnoegle",
                "funktionsnavn",
            ],
            "udvidelser": [
                "primær",
                "fraktion",
                "udvidelse_1",
                "udvidelse_2",
                "udvidelse_3",
                "udvidelse_4",
                "udvidelse_5",
                "udvidelse_6",
                "udvidelse_7",
                "udvidelse_8",
                "udvidelse_9",
                "udvidelse_10",
            ],
        },
        "attributter_metadata": {
            "egenskaber": {"brugervendtnoegle": {"mandatory": True}},
            "udvidelser": {
                "primær": {
                    "type": "boolean",
                },
                "fraktion": {
                    "type": "int",
                },
            },
        },
        "tilstande": {"gyldighed": ["Aktiv", "Inaktiv"]},
        "relationer_nul_til_en": ["organisatoriskfunktionstype", "primær"],
        "relationer_nul_til_mange": [
            "adresser",
            "opgaver",
            "tilknyttedebrugere",
            "tilknyttedeenheder",
            "tilknyttedeorganisationer",
            "tilknyttedeitsystemer",
            "tilknyttedeinteressefaellesskaber",
            "tilknyttedepersoner",
            "tilknyttedefunktioner",
            "tilknyttedeklasser",
        ],
    },
}

REAL_DB_STRUCTURE = deepcopy(DATABASE_STRUCTURE)
REAL_DB_STRUCTURE["klasse"]["attributter"]["egenskaber"].append("soegeord")
REAL_DB_STRUCTURE["klasse"]["attributter_metadata"]["egenskaber"]["soegeord"] = {
    "type": "soegeord"
}
