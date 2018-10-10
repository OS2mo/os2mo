# -- coding: utf-8 --

import unittest
from tests.helpers import load_fixture
from os2mo_data_import import adapters


class TestAdapter(unittest.TestCase):

    def setUp(self):

        self.validity = {
            "from": "1900-01-01",
            "to": "infinity"
        }

    def test_adapter_organisation(self):

        test_organisation = {
            "brugervendtnoegle": "AAD095CB-05B7-497A-8964-E2BCD3824D6E",
            "organisationsnavn": "test organisation"
        }

        converted = adapters.organisation_payload(
            organisation=test_organisation,
            municipality_code=999,
            validity=self.validity
        )

        expected = load_fixture("fixture_organisation.json")

        self.assertEqual(expected, converted)


    def test_adapter_klassifikation(self):

        test_klassifikation = {
            "brugervendtnoegle": "FDAEE71E-0772-4D13-BF19-0D01E4296992",
            "beskrivelse": "unittest",
            "kaldenavn": "test"
        }

        converted = adapters.klassifikation_payload(
            klassifikation=test_klassifikation,
            organisation_uuid="AAD095CB-05B7-497A-8964-E2BCD3824D6E",
            validity=self.validity
        )

        expected = load_fixture("fixture_klassifikation.json")

        self.assertEqual(expected, converted)

    def test_adapter_facet(self):

        test_facet = {
            "brugervendtnoegle": "0F011AB1-9F23-408E-A5D2-AE1BF2765151"
        }

        converted = adapters.facet_payload(
            facet=test_facet,
            klassifikation_uuid="FDAEE71E-0772-4D13-BF19-0D01E4296992",
            organisation_uuid="AAD095CB-05B7-497A-8964-E2BCD3824D6E",
            validity=self.validity
        )

        expected = load_fixture("fixture_facet.json")

        self.assertEqual(expected, converted)


    def test_adapter_klasse(self):
        test_klasse = {
            "brugervendtnoegle": "FDAEE71E-0772-4D13-BF19-0D01E4296992",
            "beskrivelse": "test",
            "eksempel": "python -m unittest",
            "omfang": "UNITTEST",
            "titel": "Test klasse"
        }

        converted = adapters.klasse_payload(
            klasse=test_klasse,
            facet_uuid="FDAEE71E-0772-4D13-BF19-0D01E4296992",
            organisation_uuid="AAD095CB-05B7-497A-8964-E2BCD3824D6E",
            validity=self.validity
        )

        expected = load_fixture("fixture_klasse.json")

        self.assertEqual(expected, converted)

    def test_adapter_itsystem(self):

        test_itsystem = {
            "brugervendtnoegle": "12D77A83-E793-4CC1-8AB4-0E183999E508",
            "itsystemnavn": "supercomputer"
        }

        converted = adapters.itsystem_payload(
            itsystem=test_itsystem,
            organisation_uuid="AAD095CB-05B7-497A-8964-E2BCD3824D6E",
            validity=self.validity
        )

        expected = load_fixture("fixture_itsystem.json")

        self.assertEqual(expected, converted)
