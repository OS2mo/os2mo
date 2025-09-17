# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest import skip
from unittest.mock import MagicMock
from unittest.mock import call
from unittest.mock import patch

import pytest
from oio_rest.custom_exceptions import BadRequestException
from oio_rest.db import db_helpers
from oio_rest.db import db_structure

from tests.oio_rest.util import ExtTestCase


class TestDBHelpers(ExtTestCase):
    @pytest.fixture(autouse=True)
    def setup_db_helpers(self) -> None:
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

    def test_get_attribute_fields_uses_cache(self) -> None:
        # Arrange
        expected_result = ["value1", "value2"]
        db_helpers._attribute_fields = {"test": expected_result}

        # Act
        actual_result = db_helpers.get_attribute_fields("test")

        # Assert
        assert expected_result == actual_result

    def test_get_field_type_default(self) -> None:
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

    @ExtTestCase.patch_db_struct(MagicMock())
    async def test_get_relation_field_type_default(self):
        # Arrange
        expected_result = "text"

        # Act
        actual_result = db_helpers.get_relation_field_type("attributename", "fieldname")

        # Assert
        assert expected_result == actual_result

    @ExtTestCase.patch_db_struct(
        {
            "testclass1": {
                "relationer_metadata": {
                    "*": {
                        "indeks": {"type": "int"},
                        "key1": {"type": "value_override1"},
                    },
                    "specific": {
                        "key2": {"type": "value_override2"},
                    },
                }
            }
        }
    )
    async def test_get_relation_field_type_override(self):
        # Arrange
        expected_result1 = "value_override1"
        expected_result2 = "value_override2"

        # Act
        actual_result1 = db_helpers.get_relation_field_type("testclass1", "key1")
        actual_result2 = db_helpers.get_relation_field_type("testclass1", "key2")

        # Assert
        assert expected_result1 == actual_result1
        assert expected_result2 == actual_result2

    @ExtTestCase.patch_db_struct(
        {
            "testclass1": {
                "relationer_metadata": {
                    "*": {
                        "indeks": {"type": "int"},
                        "key1": {"type": "value_override1"},
                    },
                    "specific": {
                        "key2": {"type": "value_override2"},
                    },
                }
            }
        }
    )
    async def test_get_relation_field_type_override_field_not_found(self):
        # Arrange
        expected_result = "text"

        # Act
        actual_result = db_helpers.get_relation_field_type(
            "testclass1", "unknown_override"
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

    def test_get_attribute_names_default(self) -> None:
        # Arrange
        expected_result = {
            "itsystem": ["itsystemegenskaber"],
            "bruger": ["brugeregenskaber", "brugerudvidelser"],
            "organisation": ["organisationegenskaber"],
            "sag": ["sagegenskaber"],
            "organisationfunktion": [
                "organisationfunktionegenskaber",
                "organisationfunktionudvidelser",
            ],
            "organisationenhed": ["organisationenhedegenskaber"],
            "facet": ["facetegenskaber"],
            "interessefaellesskab": ["interessefaellesskabegenskaber"],
            "loghaendelse": ["loghaendelseegenskaber"],
            "dokument": ["dokumentegenskaber"],
            "tilstand": ["tilstandegenskaber"],
            "klassifikation": ["klassifikationegenskaber"],
            "indsats": ["indsatsegenskaber"],
            "aktivitet": ["aktivitetegenskaber"],
            "klasse": ["klasseegenskaber"],
        }

        # Act
        actual_result = {
            c: db_helpers.get_attribute_names(c) for c in db_structure.REAL_DB_STRUCTURE
        }

        # Assert
        assert expected_result == actual_result

    def test_get_attribute_names_uses_cache(self) -> None:
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

    def test_get_relation_names_default(self) -> None:
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
            "sag": [
                "behandlingarkiv",
                "afleveringsarkiv",
                "primaerklasse",
                "opgaveklasse",
                "handlingsklasse",
                "kontoklasse",
                "sikkerhedsklasse",
                "foelsomhedsklasse",
                "indsatsklasse",
                "ydelsesklasse",
                "ejer",
                "ansvarlig",
                "primaerbehandler",
                "udlaanttil",
                "primaerpart",
                "ydelsesmodtager",
                "oversag",
                "praecedens",
                "afgiftsobjekt",
                "ejendomsskat",
                "andetarkiv",
                "andrebehandlere",
                "sekundaerpart",
                "andresager",
                "byggeri",
                "fredning",
                "journalpost",
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
            "interessefaellesskab": [
                "branche",
                "interessefaellesskabstype",
                "overordnet",
                "tilhoerer",
                "adresser",
                "opgaver",
                "tilknyttedebrugere",
                "tilknyttedeenheder",
                "tilknyttedefunktioner",
                "tilknyttedeinteressefaellesskaber",
                "tilknyttedeorganisationer",
                "tilknyttedepersoner",
                "tilknyttedeitsystemer",
            ],
            "loghaendelse": ["objekt", "bruger", "brugerrolle"],
            "dokument": [
                "nyrevision",
                "primaerklasse",
                "ejer",
                "ansvarlig",
                "primaerbehandler",
                "fordelttil",
                "arkiver",
                "besvarelser",
                "udgangspunkter",
                "kommentarer",
                "bilag",
                "andredokumenter",
                "andreklasser",
                "andrebehandlere",
                "parter",
                "kopiparter",
                "tilknyttedesager",
            ],
            "tilstand": [
                "tilstandsobjekt",
                "tilstandstype",
                "tilstandsvaerdi",
                "begrundelse",
                "tilstandskvalitet",
                "tilstandsvurdering",
                "tilstandsaktoer",
                "tilstandsudstyr",
                "samtykke",
                "tilstandsdokument",
            ],
            "klassifikation": ["ansvarlig", "ejer"],
            "indsats": [
                "indsatsmodtager",
                "indsatstype",
                "indsatskvalitet",
                "indsatsaktoer",
                "samtykke",
                "indsatssag",
                "indsatsdokument",
            ],
            "aktivitet": [
                "aktivitetstype",
                "emne",
                "foelsomhedklasse",
                "ansvarligklasse",
                "rekvirentklasse",
                "ansvarlig",
                "tilhoerer",
                "udfoererklasse",
                "deltagerklasse",
                "objektklasse",
                "resultatklasse",
                "grundlagklasse",
                "facilitetklasse",
                "adresse",
                "geoobjekt",
                "position",
                "facilitet",
                "lokale",
                "aktivitetdokument",
                "aktivitetgrundlag",
                "aktivitetresultat",
                "udfoerer",
                "deltager",
            ],
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

    def test_get_relation_names_uses_cache(self) -> None:
        # Arrange

        expected_result = ["value1", "value2", "value3", "value4"]
        db_helpers._relation_names = {"testclass1": expected_result}

        # Act
        actual_result = db_helpers.get_relation_names("testclass1")

        # Assert
        assert expected_result == actual_result

    def test_get_state_names_order(self) -> None:
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
            "sag": [
                "fremdrift",
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
            "interessefaellesskab": [
                "gyldighed",
            ],
            "loghaendelse": [
                "gyldighed",
            ],
            "dokument": [
                "fremdrift",
            ],
            "tilstand": [
                "status",
                "publiceret",
            ],
            "klassifikation": [
                "publiceret",
            ],
            "indsats": [
                "publiceret",
                "fremdrift",
            ],
            "aktivitet": [
                "status",
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

    def test_get_state_names_default(self) -> None:
        # Arrange
        expected_result = {
            "itsystem": [
                "gyldighed",
            ],
            "bruger": ["gyldighed"],
            "organisation": ["gyldighed"],
            "sag": ["fremdrift"],
            "organisationfunktion": ["gyldighed"],
            "organisationenhed": ["gyldighed"],
            "facet": ["publiceret"],
            "interessefaellesskab": ["gyldighed"],
            "loghaendelse": ["gyldighed"],
            "dokument": ["fremdrift"],
            "tilstand": ["status", "publiceret"],
            "klassifikation": ["publiceret"],
            "indsats": ["publiceret", "fremdrift"],
            "aktivitet": ["status", "publiceret"],
            "klasse": ["publiceret"],
        }

        # Act
        actual_result = {
            c: db_helpers.get_state_names(c) for c in db_structure.REAL_DB_STRUCTURE
        }

        # Assert
        assert expected_result == actual_result

    def test_input_list(self) -> None:
        # Arrange
        _type = MagicMock()
        _type.input.return_value = "listvalue"

        input = {"testkey": ["item1", "item2"]}

        expected_result = ["listvalue", "listvalue"]

        expected_args = [call("item1"), call("item2")]

        # Act
        actual_result = db_helpers.input_list(_type, input, "testkey")

        # Assert
        assert expected_result == actual_result
        assert _type.input.call_count == 2
        assert expected_args == _type.input.call_args_list

    def test_input_list_none_value(self) -> None:
        # Arrange
        _type = MagicMock()
        _type.input.return_value = "generatorvalue"

        input = {"testkey": None}
        # Act
        actual_result = db_helpers.input_list("", input, "testkey")
        # Assert
        assert actual_result is None

    def test_input_dict_list(self) -> None:
        # Arrange
        _type = MagicMock()
        _type.input.return_value = "generatorvalue"

        input = {"testkey": ["value1", "value2"]}

        expected_result = ["generatorvalue", "generatorvalue"]

        expected_args = [call("testkey", "value1"), call("testkey", "value2")]

        # Act
        actual_result = db_helpers.input_dict_list(_type, input)

        # Assert
        assert expected_result == actual_result
        assert _type.input.call_count == 2
        assert expected_args == _type.input.call_args_list

    def test_input_dict_list_none_value(self) -> None:
        # Arrange
        _type = MagicMock()
        _type.input.return_value = "generatorvalue"

        input = None

        expected_result = None

        # Act
        actual_result = db_helpers.input_dict_list(_type, input)

        # Assert
        assert expected_result == actual_result

    def test_to_bool_correctly_parses_bools(self) -> None:
        # Arrange
        # Act
        actual_true = db_helpers.to_bool(True)
        actual_false = db_helpers.to_bool(False)
        # Assert
        assert actual_true
        assert not actual_false

    def test_to_bool_correctly_parses_true_strings(self) -> None:
        # Arrange
        # Act
        actual_true_capital = db_helpers.to_bool("True")
        actual_true_lc = db_helpers.to_bool("true")
        actual_true_one = db_helpers.to_bool("1")

        # Assert
        assert actual_true_capital
        assert actual_true_lc
        assert actual_true_one

    def test_to_bool_correctly_parses_false_strings(self) -> None:
        # Arrange
        # Act
        actual_false_capital = db_helpers.to_bool("False")
        actual_false_lc = db_helpers.to_bool("false")
        actual_false_one = db_helpers.to_bool("0")

        # Assert
        assert not actual_false_capital
        assert not actual_false_lc
        assert not actual_false_one

    def test_to_bool_handles_none(self) -> None:
        # Arrange
        expected_result = None
        # Act
        actual_result = db_helpers.to_bool(None)

        # Assert
        assert expected_result == actual_result

    def test_to_bool_raises_on_invalid_value(self) -> None:
        # Arrange
        # Act & Assert
        with pytest.raises(ValueError):
            db_helpers.to_bool("This is not a valid boolean value")

    def test_dokumentvarianttype_input_when_none(self) -> None:
        from oio_rest.db.db_helpers import DokumentVariantType

        # Arrange
        expected_result = None

        # Act
        actual_result = DokumentVariantType.input(None)

        # Assert
        assert expected_result == actual_result

    def test_dokumentvariantegenskabertype_input_when_none(self) -> None:
        from oio_rest.db.db_helpers import DokumentVariantEgenskaberType

        # Arrange
        expected_result = None

        # Act
        actual_result = DokumentVariantEgenskaberType.input(None)

        # Assert
        assert expected_result == actual_result

    def test_dokumentdeltype_input_when_none(self) -> None:
        from oio_rest.db.db_helpers import DokumentDelType

        # Arrange
        expected_result = None

        # Act
        actual_result = DokumentDelType.input(None)

        # Assert
        assert expected_result == actual_result

    def test_virkning_input_when_none(self) -> None:
        from oio_rest.db.db_helpers import Virkning

        # Arrange
        expected_result = None

        # Act
        actual_result = Virkning.input(None)

        # Assert
        assert expected_result == actual_result

    @skip("Document support destroyed when introducint FastAPI")
    def test_dokumentdelegenskabertype_get_file_storage_raises_bre(self) -> None:
        from oio_rest.db.db_helpers import DokumentDelEgenskaberType

        # Arrange
        app = MagicMock()

        # Act
        with (
            app.test_request_context(params={}, method="POST"),
            self.assertRaises(BadRequestException),
        ):
            DokumentDelEgenskaberType._get_file_storage_for_content_url(
                "field:not_in_request"
            )

    @skip("Document support destroyed when introducint FastAPI")
    def test_dokumentdelegenskabertype_get_file_storage(self) -> None:
        from oio_rest.db.db_helpers import DokumentDelEgenskaberType

        # Arrange
        mockfile = MagicMock()
        app = MagicMock()
        request = MagicMock()

        # Act
        with app.test_request_context(data={}, method="POST"):
            request.files = {"testfile": mockfile}

            actual_result = DokumentDelEgenskaberType._get_file_storage_for_content_url(
                "field:testfile"
            )

        # Assert
        assert mockfile == actual_result

    def test_dokumentdelegenskabertype_get_file_storage_returns_none(self) -> None:
        from oio_rest.db.db_helpers import DokumentDelEgenskaberType

        # Arrange

        # Act
        actual_result = DokumentDelEgenskaberType._get_file_storage_for_content_url(
            "notfield:testfile"
        )

        # Assert
        assert actual_result is None

    @skip("Document support destroyed when introducint FastAPI")
    @patch(
        "oio_rest.db.db_helpers.DokumentDelEgenskaberType"
        "._get_file_storage_for_content_url"
    )
    @patch("oio_rest.db.db_helpers.content_store.save_file_object")
    def test_dokumentdelegenskabertype_input_update_file(
        self, mock_save_file, mock_get_file
    ) -> None:
        # type: (MagicMock, MagicMock) -> None
        from oio_rest.db.db_helpers import DokumentDelEgenskaberType

        # Arrange
        app = MagicMock()

        inputdata = {"indhold": "field:testdata"}

        mock_get_file.return_value = mockfile = MagicMock()

        # Act
        with app.test_request_context(method="POST"):
            DokumentDelEgenskaberType.input(inputdata)

        # Assert
        mock_get_file.assert_called_with("field:testdata")
        mock_save_file.assert_called_with(mockfile)

    def test_dokumentdelegenskabertype_input_when_none(self) -> None:
        from oio_rest.db.db_helpers import DokumentDelEgenskaberType

        # Arrange
        expected_result = None

        # Act
        actual_result = DokumentDelEgenskaberType.input(None)

        # Assert
        assert expected_result == actual_result

    def test_dokumentdelrelationtype_input_when_none(self) -> None:
        from oio_rest.db.db_helpers import DokumentDelRelationType

        # Arrange
        expected_result = None

        # Act
        actual_result = DokumentDelRelationType.input("key", None)

        # Assert
        assert expected_result == actual_result


class TestSearchable:
    def test_searchable_get_fields(self) -> None:
        # Arrange
        from oio_rest.db.db_helpers import Searchable

        class TestSearchableClass(Searchable):
            _fields = ("field1", "field2")

        expected_result = ("field1", "field2")

        # Act
        actual_result = TestSearchableClass.get_fields()

        # Assert
        assert expected_result == actual_result

    def test_searchable_get_fields_with_virkning(self) -> None:
        # Arrange
        from oio_rest.db.db_helpers import Searchable

        class TestSearchableClass(Searchable):
            _fields = ("field1", "field2", "virkning")

        expected_result = ("field1", "field2")

        # Act
        actual_result = TestSearchableClass.get_fields()

        # Assert - Cast to set for comparison,
        # as result is converted from set with no ordering
        assert set(expected_result) == set(actual_result)
