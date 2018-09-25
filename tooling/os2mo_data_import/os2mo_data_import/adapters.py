# -- coding: utf-8 --


def validity_range(date_from, date_to):

    return {
        "from": date_from,
        "to": date_to
    }


def build_organisation_payload(name, user_key, uuid=None, municipality_code=999,
                  date_from="1900-01-01", date_to="infinity"):

        # Inelegant conversion to string
        municipality_code = str(municipality_code)

        # Create urn value
        urn_municipality_code = "urn:dk:kommune:{}".format(municipality_code)

        attributter = {
            "organisationegenskaber": [
                {
                    "brugervendtnoegle": str(user_key),
                    "organisationsnavn": str(name),
                    "virkning": validity_range(date_from, date_to)
                }
            ]
        }

        relationer = {
            "myndighed": [
                {
                    "urn": urn_municipality_code,
                    "virkning": validity_range(date_from, date_to)
                }
            ]
        }

        tilstande = {
            "organisationgyldighed": [
                {
                    "gyldighed": "Aktiv",
                    "virkning": validity_range(date_from, date_to)
                }
            ]
        }

        return {
            "note": "Automatisk indlæsning",
            "attributter": attributter,
            "relationer": relationer,
            "tilstande": tilstande
    }


def build_facet_payload(brugervendtnoegle, parent_org, date_from, date_to="infinity"):

    attributter = {
        "facetegenskaber": [
            {
                "brugervendtnoegle": str(brugervendtnoegle),
                "virkning": validity_range(date_from, date_to)
            }
        ]
    }

    relationer = {
        "ansvarlig": [
            {
                "objekttype": "organisation",
                "uuid": parent_org,
                "virkning": validity_range(date_from, date_to)
            }
        ],
        "facettilhoerer": [
            {
                "objekttype": "klassifikation",
                "virkning": validity_range(date_from, date_to)
            }
        ]
    }

    tilstande = {
        "facetpubliceret": [
            {
                "publiceret": "Publiceret",
                "virkning": validity_range(date_from, date_to)
            }
        ]
    }

    return {
        "attributter": attributter,
        "relationer": relationer,
        "tilstande": tilstande
    }


def build_klasse_payload(brugervendtnoegle, facet_ref, parent_org,
                  date_from, date_to="infinity", **properties):

        klasse_properties = {
            "brugervendtnoegle": brugervendtnoegle,
            "virkning": validity_range(date_from, date_to)
        }

        if properties:
            klasse_properties.update(properties)

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
                    "virkning": validity_range(date_from, date_to)
                }
            ],
            "facet": [
                {
                    "objekttype": "facet",
                    "uuid": str(facet_ref),
                    "virkning": validity_range(date_from, date_to)
                }
            ]
        }

        tilstande = {
            "klassepubliceret": [
                {
                    "publiceret": "Publiceret",
                    "virkning": validity_range(date_from, date_to)
                }
            ]
        }

        return {
            "attributter": attributter,
            "relationer": relationer,
            "tilstande": tilstande
}


def build_org_unit_payload(name, parent_uuid, type_uuid, date_from, date_to=None):

    return {
        "name": str(name),
        "parent": {
            "uuid": str(parent_uuid)
        },
        "org_unit_type": {
            "uuid": str(type_uuid)
        },
        "validity": {
            "from": date_from,
            "to": date_to
        }
    }


def build_employee_payload(name, cpr_no, org_ref, user_key, date_from, date_to=None):

    return {
        "name": name,
        "user_key": user_key,
        "cpr_no": cpr_no,
        "org": {
            "uuid": org_ref
        },
        "validity": {
            "from": date_from,
            "to": date_to
        }
    }


