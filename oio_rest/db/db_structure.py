# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import collections
import itertools
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

DB_TEMPLATE_EXTRA_OPTIONS = {}


def merge_objects(a, b):  # pragma: no cover
    """
    Merge two objects of the same type. Supports lists and dicts.
    Recursively merges internal lists and dictionaries.
    :param a: The first object
    :param b: The second object
    :return: A merged object
    """
    assert type(a) is type(b), "type mismatch!: {} != {}".format(
        type(a),
        type(b),
    )

    if isinstance(a, dict) and isinstance(b, dict):
        return _merge_dicts(a, b)

    elif isinstance(a, list) and isinstance(b, list):
        return _merge_lists(a, b)

    else:
        raise AttributeError(f"Unsupported parameter type {type(a)}")


def _merge_lists(a: list, b: list):  # pragma: no cover
    """
    Merges two lists and removes duplicates
    :param a: The first list
    :param b: The second list
    :return: A merged list with duplicates removed
    """
    return list(set(a + b))


def _merge_dicts(a: dict, b: dict):  # pragma: no cover
    """
    Merges two dicts, retaining ordering.
    :param a: The first dict
    :param b: The second dict
    :return: A merged dict
    """
    if a is None:
        return b
    elif b is None:
        return a

    # the database code relies on the ordering of elements, so ensure
    # that a consistent ordering, even on Python 3.5
    return collections.OrderedDict(
        (k, b[k] if k not in a else a[k] if k not in b else merge_objects(a[k], b[k]))
        for k in itertools.chain(a, b)
    )


if __name__ == "__main__":  # pragma: no cover
    export_structure = "\n".join(sorted(REAL_DB_STRUCTURE))
    print(export_structure)
