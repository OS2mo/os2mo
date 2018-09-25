# -- coding: utf-8 --


def validity_range(date_from, date_to):

    return {
        "from": date_from,
        "to": date_to
    }


def build_payload(name, user_key, municipality_code=999,
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


def build_facet_payload(user_key, parent_org, from_date, to_date="infinity"):

    attributter = {
        "facetegenskaber": [
            {
                "brugervendtnoegle": str(user_key),
                "virkning": validity_range(from_date, to_date)
            }
        ]
    }

    relationer = {
        "ansvarlig": [
            {
                "objekttype": "organisation",
                "uuid": parent_org,
                "virkning": validity_range(from_date, to_date)
            }
        ],
        "facettilhoerer": [
            {
                "objekttype": "klassifikation",
                "virkning": validity_range(from_date, to_date)
            }
        ]
    }

    tilstande = {
        "facetpubliceret": [
            {
                "publiceret": "Publiceret",
                "virkning": validity_range(from_date, to_date)
            }
        ]
    }

    return {
        "attributter": attributter,
        "relationer": relationer,
        "tilstande": tilstande
    }


def build_klasse_payload(user_key, facet_ref, parent_org,
                  date_from, date_to="infinity", **properties):

        klasse_properties = {
            "brugervendtnoegle": user_key,
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
                    "uuid": facet_ref,
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


if __name__ == "__main__":

    facet = build_facet_payload(
        user_key="asdfasdf",
        parent_org="asdfasdfasdf",
        from_date="1900-01-01",
        to_date="infinity"
    )

    print(facet)


    klasse = build_klasse_payload(
                user_key="sdfasdfasdf",
                facet_ref="sadfasdfasdfasdf",
                parent_org="asdfasdfasdf",
                date_from="1900-01-01",
                date_to="infinity",
            )
    print(klasse)
