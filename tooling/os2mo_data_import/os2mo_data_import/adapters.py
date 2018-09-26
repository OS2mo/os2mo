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


def build_facet_payload(facet, parent_org):
    """

    :param facet:
    :param parent_org:
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
                "uuid": parent_org,
                "virkning": validity
            }
        ],
        "facettilhoerer": [
            {
                "objekttype": "klassifikation",
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


def build_klasse_payload(klasse, facet_ref, parent_org):
    """

    :param klasse:
    :param parent_org:
    :return:
    """

    brugervendtnoegle = klasse["brugervendtnoegle"]
    validity = klasse["validity"]

    klasse_properties = {
        "brugervendtnoegle": str(brugervendtnoegle),
        "virkning": validity
    }

    attributter = {
        "klasseegenskaber": [
            klasse_properties
        ]
    }

    relationer = {
        "ansvarlig": [
            {
                "objekttype": "organisation",
                "uuid": parent_org,
                "virkning": validity
            }
        ],
        "facet": [
            {
                "objekttype": "facet",
                "uuid": str(facet_ref),
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
