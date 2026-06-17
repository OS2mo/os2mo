# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest

from oio_rest.db import db_helpers
from oio_rest.db import db_structure
from tests.oio_rest.util import ExtTestCase


class TestDBHelpers(ExtTestCase):
    @pytest.fixture(autouse=True)
    def setup_db_helpers(self):
        db_helpers._attribute_fields = {}
        db_helpers._attribute_names = {}
        db_helpers._relation_names = {}

    @ExtTestCase.patch_db_struct(
        {
            "testclass1": {"attributter": {"testattribut": ["value1", "value2"]}},
            "testclass2": {"attributter": {"testattribut": ["value3", "value4"]}},
        }
    )
    async def test_get_attribute_reads_db_struct(self):
        # Arrange
        expected_fields = {
            "testclass1testattribut": ["value1", "value2", "virkning"],
            "testclass2testattribut": ["value3", "value4", "virkning"],
        }

        expected_result = ["value1", "value2", "virkning"]

        # Act
        actual_result = db_helpers.get_attribute_fields("testclass1testattribut")
        actual_fields = db_helpers._attribute_fields

        # Assert
        assert expected_fields == actual_fields
        assert expected_result == actual_result

    def test_get_attribute_fields_uses_cache(self):
        # Arrange
        expected_result = ["value1", "value2"]
        db_helpers._attribute_fields = {"test": expected_result}

        # Act
        actual_result = db_helpers.get_attribute_fields("test")

        # Assert
        assert expected_result == actual_result

    def test_get_field_type_default(self):
        # Arrange
        expected_result = "text"

        # Act
        actual_result = db_helpers.get_field_type("attributename", "fieldname")

        # Assert
        assert expected_result == actual_result

    @ExtTestCase.patch_db_struct(
        {
            "testclass1": {
                "attributter_metadata": {
                    "testattribut": {"value": {"type": "value_override"}}
                }
            }
        }
    )
    async def test_get_field_type_override(self):
        # Arrange
        expected_result = "value_override"

        # Act
        actual_result = db_helpers.get_field_type("testclass1testattribut", "value")

        # Assert
        assert expected_result == actual_result

    @ExtTestCase.patch_db_struct(
        {
            "testclass1": {
                "attributter_metadata": {
                    "testattribut": {"value": {"type": "value_override"}}
                }
            }
        }
    )
    async def test_get_field_type_override_field_not_found(self):
        # Arrange
        expected_result = "text"

        # Act
        actual_result = db_helpers.get_field_type(
            "testclass1testattribut", "unknown_override"
        )

        # Assert
        assert expected_result == actual_result

    @ExtTestCase.patch_db_struct(
        {
            "testclass1": {
                "attributter": {
                    "testattribut1": ["value1", "value2"],
                    "testattribut2": ["value3", "value4"],
                }
            }
        }
    )
    async def test_get_attribute_names_reads_db_struct(self):
        # Arrange
        expected_result = ["testclass1testattribut1", "testclass1testattribut2"]

        # Act
        actual_result = db_helpers.get_attribute_names("testclass1")

        # Assert
        assert expected_result == actual_result

    def test_get_attribute_names_default(self):
        # Arrange
        expected_result = {
            "itsystem": ["itsystemegenskaber"],
            "bruger": ["brugeregenskaber", "brugerudvidelser"],
            "organisation": ["organisationegenskaber"],
            "organisationfunktion": [
                "organisationfunktionegenskaber",
                "organisationfunktionudvidelser",
            ],
            "organisationenhed": ["organisationenhedegenskaber"],
            "facet": ["facetegenskaber"],
            "klassifikation": ["klassifikationegenskaber"],
            "klasse": ["klasseegenskaber"],
        }

        # Act
        actual_result = {
            c: db_helpers.get_attribute_names(c) for c in db_structure.REAL_DB_STRUCTURE
        }

        # Assert
        assert expected_result == actual_result

    def test_get_attribute_names_uses_cache(self):
        # Arrange
        expected_result = ["value1", "value2"]
        db_helpers._attribute_names = {"testclass1": expected_result}

        # Act
        actual_result = db_helpers.get_attribute_names("testclass1")

        # Assert
        assert expected_result == actual_result

    async def test_get_state_names(self):
        async with self.patch_db_struct(
            {
                "testclass1": {
                    "tilstande": {
                        "testtilstand1": ["value1", "value2"],
                        "testtilstand2": ["value3", "value4"],
                    }
                }
            }
        ):
            # Arrange
            expected_result = [
                "testtilstand1",
                "testtilstand2",
            ]

            # Act
            actual_result = db_helpers.get_state_names("testclass1")

            # Assert
            assert expected_result == sorted(actual_result)

        async with self.patch_db_struct(
            {
                "testclass1": {
                    "tilstande": [
                        ("testtilstand1", ["value1", "value2"]),
                        ("testtilstand2", ["value3", "value4"]),
                    ],
                },
            }
        ):
            # Arrange
            expected_result = [
                "testtilstand1",
                "testtilstand2",
            ]

            # Act
            actual_result = db_helpers.get_state_names("testclass1")

            # Assert
            assert expected_result == actual_result

    @ExtTestCase.patch_db_struct(
        {
            "testclass1": {
                "relationer_nul_til_en": ["value1", "value2"],
                "relationer_nul_til_mange": ["value3", "value4"],
            }
        }
    )
    async def test_get_relation_names(self):
        # Arrange
        expected_result = ["value1", "value2", "value3", "value4"]

        # Act
        actual_result = db_helpers.get_relation_names("testclass1")

        # Assert
        assert expected_result == actual_result

    def test_get_relation_names_default(self):
        # Arrange
        expected_result = {
            "itsystem": [
                "tilhoerer",
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
            "bruger": [
                "tilhoerer",
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
            "organisation": [
                "branche",
                "myndighed",
                "myndighedstype",
                "overordnet",
                "produktionsenhed",
                "skatteenhed",
                "tilhoerer",
                "virksomhed",
                "virksomhedstype",
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
            "organisationfunktion": [
                "organisatoriskfunktionstype",
                "primær",
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
            "organisationenhed": [
                "branche",
                "enhedstype",
                "overordnet",
                "produktionsenhed",
                "skatteenhed",
                "tilhoerer",
                "niveau",
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
            "facet": ["ansvarlig", "ejer", "facettilhoerer", "redaktoerer"],
            "klassifikation": ["ansvarlig", "ejer"],
            "klasse": [
                "ejer",
                "ansvarlig",
                "overordnetklasse",
                "facet",
                "redaktoerer",
                "sideordnede",
                "mapninger",
                "tilfoejelser",
                "erstatter",
                "lovligekombinationer",
            ],
        }

        # Act
        actual_result = {
            c: db_helpers.get_relation_names(c) for c in db_structure.REAL_DB_STRUCTURE
        }

        # Assert
        assert expected_result == actual_result

    def test_get_relation_names_uses_cache(self):
        # Arrange

        expected_result = ["value1", "value2", "value3", "value4"]
        db_helpers._relation_names = {"testclass1": expected_result}

        # Act
        actual_result = db_helpers.get_relation_names("testclass1")

        # Assert
        assert expected_result == actual_result

    def test_get_state_names_order(self):
        # Arrange
        expected_result = {
            "itsystem": [
                "gyldighed",
            ],
            "bruger": [
                "gyldighed",
            ],
            "organisation": [
                "gyldighed",
            ],
            "organisationfunktion": [
                "gyldighed",
            ],
            "organisationenhed": [
                "gyldighed",
            ],
            "facet": [
                "publiceret",
            ],
            "klassifikation": [
                "publiceret",
            ],
            "klasse": [
                "publiceret",
            ],
        }

        # Act
        actual_result = {
            c: list(db_helpers.get_state_names(c))
            for c in db_structure.REAL_DB_STRUCTURE
        }

        # Assert
        assert expected_result == actual_result

    def test_get_state_names_default(self):
        # Arrange
        expected_result = {
            "itsystem": [
                "gyldighed",
            ],
            "bruger": ["gyldighed"],
            "organisation": ["gyldighed"],
            "organisationfunktion": ["gyldighed"],
            "organisationenhed": ["gyldighed"],
            "facet": ["publiceret"],
            "klassifikation": ["publiceret"],
            "klasse": ["publiceret"],
        }

        # Act
        actual_result = {
            c: db_helpers.get_state_names(c) for c in db_structure.REAL_DB_STRUCTURE
        }

        # Assert
        assert expected_result == actual_result

    def test_to_bool_correctly_parses_bools(self):
        # Arrange
        # Act
        actual_true = db_helpers.to_bool(True)
        actual_false = db_helpers.to_bool(False)
        # Assert
        assert actual_true
        assert not actual_false

    def test_to_bool_correctly_parses_true_strings(self):
        # Arrange
        # Act
        actual_true_capital = db_helpers.to_bool("True")
        actual_true_lc = db_helpers.to_bool("true")
        actual_true_one = db_helpers.to_bool("1")

        # Assert
        assert actual_true_capital
        assert actual_true_lc
        assert actual_true_one

    def test_to_bool_correctly_parses_false_strings(self):
        # Arrange
        # Act
        actual_false_capital = db_helpers.to_bool("False")
        actual_false_lc = db_helpers.to_bool("false")
        actual_false_one = db_helpers.to_bool("0")

        # Assert
        assert not actual_false_capital
        assert not actual_false_lc
        assert not actual_false_one

    def test_to_bool_handles_none(self):
        # Arrange
        expected_result = None
        # Act
        actual_result = db_helpers.to_bool(None)

        # Assert
        assert expected_result == actual_result

    def test_to_bool_raises_on_invalid_value(self):
        # Arrange
        # Act & Assert
        with pytest.raises(ValueError):
            db_helpers.to_bool("This is not a valid boolean value")

    def test_virkning_input_when_none(self):
        from oio_rest.db.db_helpers import Virkning

        # Arrange
        expected_result = None

        # Act
        actual_result = Virkning.input(None)

        # Assert
        assert expected_result == actual_result
