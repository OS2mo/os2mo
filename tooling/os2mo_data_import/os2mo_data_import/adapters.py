# -- coding: utf-8 --


def build_organisation_payload(organisation):
        """

        :param organisation:    Data object (Type: dict)
                                Example:

                                {
                                    "uuid": self.uuid,
                                    "name": self.name,
                                    "user_key": self.user_key,
                                    "municipality_code": self.municipality_code,
                                    "validity": self.validity
                                }
        :return:                Payload
        :rtype:                 dict
        """


        # Map
        uuid = organisation["uuid"]
        name = organisation["name"]
        user_key = organisation["user_key"]
        municipality_code = organisation["municipality_code"]
        validity = organisation["validity"]

        # Create urn value
        urn_municipality_code = "urn:dk:kommune:{code}".format(
            code=str(municipality_code)
        )

        attributter = {
            "organisationegenskaber": [
                {
                    "brugervendtnoegle": str(user_key or name),
                    "organisationsnavn": str(name),
                    "virkning": validity
                }
            ]
        }

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


def build_klassifikation_payload(klassifikation, organisation_uuid):

    # Map
    brugervendtnoegle = klassifikation["brugervendtnoegle"]
    beskrivelse = klassifikation["beskrivelse"]
    kaldenavn = klassifikation["kaldenavn"]
    validity = klassifikation["validity"]

    attributter = {
        "klassifikationegenskaber": [
            {
                "brugervendtnoegle": str(brugervendtnoegle),
                "beskrivelse": str(beskrivelse),
                "kaldenavn": str(kaldenavn),
                "virkning": validity
            }
        ]
    }

    relationer = {
        "ansvarlig": [
            {
                "objekttype": "organisation",
                "uuid": str(organisation_uuid),
                "virkning": validity
            }
        ],
        "ejer": [
            {
                "objekttype": "organisation",
                "uuid": str(organisation_uuid),
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


def build_facet_payload(facet, klassifikation_uuid, organisation_uuid):
    """

    :param facet:
    :param organisation_uuid:
    :return:
    """

    # Map
    brugervendtnoegle = facet["brugervendtnoegle"]
    validity = facet["validity"]

    attributter = {
        "facetegenskaber": [
            {
                "brugervendtnoegle": str(brugervendtnoegle),
                "virkning": validity
            }
        ]
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


def build_klasse_payload(klasse, facet_uuid, organisation_uuid):
    """

    :param klasse:
    :param organisation_uuid:
    :return:
    """

    validity = klasse.pop("validity")
    brugervendtnoegle = klasse["brugervendtnoegle"]
    title = klasse.get("titel")

    klasse_properties = {
        "titel": (title or brugervendtnoegle),
        "virkning": validity
    }

    klasse_properties.update(klasse)

    attributter = {
        "klasseegenskaber": [
            klasse_properties
        ]
    }

    relationer = {
        "ansvarlig": [
            {
                "objekttype": "organisation",
                "uuid": str(organisation_uuid),
                "virkning": validity
            }
        ],
        "facet": [
            {
                "objekttype": "facet",
                "uuid": str(facet_uuid),
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


def build_itsystem_payload(itsystem, organisation_uuid):
    system_name = itsystem["system_name"]
    user_key = itsystem["user_key"]
    validity = itsystem["validity"]

    attributter = {
        "itsystemegenskaber": [
            {
                "brugervendtnoegle": str(system_name),
                "itsystemnavn": str(user_key),
                "virkning": validity
            }
        ]
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
