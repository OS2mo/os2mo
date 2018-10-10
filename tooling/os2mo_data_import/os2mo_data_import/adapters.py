# -- coding: utf-8 --


def organisation_payload(organisation, municipality_code, validity):
        """
        MOX/Lora paylod for organisation

        :param organisation:
            Data object: Organisation (dict)
            Example:
                {
                    "name": "Magenta Aps,
                    "user_key": "ABC34D61-FB3F-451A-9299-31218B4570E6",
                    "municipality_code": 101,
                }

        :param validity:
            Start and end date (dict)
            Example:
                {
                    "from": "1900-01-01",
                    "to": "infinity"
                }

        :return:
            POST data payload (dict)

        """

        properties = {
            "virkning": validity
        }

        properties.update(organisation)

        attributter = {
            "organisationegenskaber": [properties]
        }

        # Create urn value
        urn_municipality_code = "urn:dk:kommune:{code}".format(
            code=str(municipality_code)
        )

        relationer = {
            "myndighed": [
                {
                    "urn": urn_municipality_code,
                    "virkning": validity
                }
            ]
        }

        tilstande = {
            "organisationgyldighed": [
                {
                    "gyldighed": "Aktiv",
                    "virkning": validity
                }
            ]
        }

        return {
            "note": "Automatisk indlæsning",
            "attributter": attributter,
            "relationer": relationer,
            "tilstande": tilstande
    }


def klassifikation_payload(klassifikation, organisation_uuid, validity):
    """
    MOX/Lora paylod for klassifikation

    :param klassifikation:
         Data object: Klassifikation (dict)

    :param organisation_uuid:
        UUID of the organisation wrapper (str: uuid)

    :param validity:
        Start and end date (dict)
        Example:
            {
                "from": "1900-01-01",
                "to": "infinity"
            }

    :return:
        OIO formatted post data payload (dict)

    """

    properties = {
        "virkning": validity
    }

    properties.update(klassifikation)

    attributter = {
        "klassifikationegenskaber": [properties]
    }

    relationer = {
        "ansvarlig": [
            {
                "objekttype": "organisation",
                "uuid": organisation_uuid,
                "virkning": validity
            }
        ],
        "ejer": [
            {
                "objekttype": "organisation",
                "uuid": organisation_uuid,
                "virkning": validity
            }
        ]
    }

    tilstande = {
        "klassifikationpubliceret": [
            {
                "publiceret": "Publiceret",
                "virkning": validity
            }
        ]
    }

    return {
        "attributter": attributter,
        "relationer": relationer,
        "tilstande": tilstande
    }


def facet_payload(facet, klassifikation_uuid, organisation_uuid, validity):
    """
    MOX/Lora paylod for facet

    :param facet:
         Data object: facet (dict)

    :param klassifikation_uuid:
        UUID of the parent type: klassifikation (str: uuid)

    :param organisation_uuid:
        UUID of the organisation wrapper (str: uuid)

    :param validity:
        Start and end date (dict)
        Example:
            {
                "from": "1900-01-01",
                "to": "infinity"
            }

    :return:
        OIO formatted post data payload (dict)

    """

    properties = {
        "virkning": validity
    }

    properties.update(facet)

    attributter = {
        "facetegenskaber": [properties]
    }

    relationer = {
        "ansvarlig": [
            {
                "objekttype": "organisation",
                "uuid": str(organisation_uuid),
                "virkning": validity
            }
        ],
        "facettilhoerer": [
            {
                "objekttype": "klassifikation",
                "uuid": str(klassifikation_uuid),
                "virkning": validity
            }
        ]
    }

    tilstande = {
        "facetpubliceret": [
            {
                "publiceret": "Publiceret",
                "virkning": validity
            }
        ]
    }

    return {
        "attributter": attributter,
        "relationer": relationer,
        "tilstande": tilstande
    }


def klasse_payload(klasse, facet_uuid, organisation_uuid, validity):
    """
    MOX/Lora paylod for klasse

    :param klasse:
         Data object: klasse (dict)

    :param facet_uuid:
        UUID of the parent type: facet (str: uuid)

    :param organisation_uuid:
        UUID of the organisation wrapper (str: uuid)

    :param validity:
        Start and end date (dict)
        Example:
            {
                "from": "1900-01-01",
                "to": "infinity"
            }

    :return:
        OIO formatted post data payload (dict)

    """

    # The following keys are required:
    if "brugervendtnøgle" and "titel" not in klasse:
        raise ValueError("Required values missing for type klasse")

    properties = {
        "virkning": validity
    }

    # Add all user specified properties
    properties.update(klasse)

    attributter = {
        "klasseegenskaber": [properties]
    }

    relationer = {
        "ansvarlig": [
            {
                "objekttype": "organisation",
                "uuid": organisation_uuid,
                "virkning": validity
            }
        ],
        "facet": [
            {
                "objekttype": "facet",
                "uuid": facet_uuid,
                "virkning": validity
            }
        ]
    }

    tilstande = {
        "klassepubliceret": [
            {
                "publiceret": "Publiceret",
                "virkning": validity
            }
        ]
    }

    return {
        "attributter": attributter,
        "relationer": relationer,
        "tilstande": tilstande
}


def itsystem_payload(itsystem, organisation_uuid, validity):
    """
    MOX/Lora paylod for itsystem

    :param itsystem:
         Data object: klasse (dict)

    :param organisation_uuid:
        UUID of the organisation wrapper (str: uuid)

    :param validity:
        Start and end date (dict)
        Example:
            {
                "from": "1900-01-01",
                "to": "infinity"
            }

    :return:
        OIO formatted post data payload (dict)

    """

    properties = {
        "virkning": validity
    }

    properties.update(itsystem)

    attributter = {
        "itsystemegenskaber": [properties]
    }

    relationer = {
        "tilhoerer": [
            {
                "uuid": str(organisation_uuid),
                "virkning": validity
            }
        ]
    }

    tilstande = {
        "itsystemgyldighed": [
            {
                "gyldighed": "Aktiv",
                "virkning": validity
            }
        ]
    }

    return {
        "attributter": attributter,
        "relationer": relationer,
        "tilstande": tilstande
    }
