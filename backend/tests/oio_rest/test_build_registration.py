# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from oio_rest import utils


class TestBuildRegistration:
    def test_is_urn_returns_true_when_string_begins_with_urn(self):
        urn1 = "urn:thisisaurn"
        assert utils.is_urn(urn1)

        urn2 = "URN:thisisaurn"
        assert utils.is_urn(urn2)

    def test_is_urn_returns_false_when_string_does_not_begin_with_urn(self):
        urn = "this is not a urn"
        assert not utils.is_urn(urn)

    def test_is_uuid_returns_true_when_string_is_uuid(self):
        uuid = "c97e1dee-1477-4dd4-a2e6-0bfc6b6b04da"
        assert utils.is_uuid(uuid)

    def test_is_uuid_returns_false_when_string_is_not_uuid(self):
        uuid = "notuuid"
        assert not utils.is_uuid(uuid)

    def test_escape_underscores(self):
        # Arrange
        value = "a_string_with_underscores"

        expected_result = r"a\_string\_with\_underscores"
        # Act
        actual_result = utils.escape_underscores(value)
        # Assert
        assert expected_result == actual_result

    def test_escape_underscores_if_none(self):
        # Arrange
        value = None

        # Act
        actual_result = utils.escape_underscores(value)
        # Assert
        assert value == actual_result

    def test_build_relation_builds_correct_relation_with_uuid_value(self):
        virkning = "VIRKNING"
        objekttype = "OBJEKTTYPE"

        value = "e16f42c5-cd64-411d-827a-15c9198e932d"

        expected_relation = {
            "virkning": virkning,
            "objekttype": objekttype,
            "uuid": value,
        }

        actual_relation = utils.build_relation(
            value=value, virkning=virkning, objekttype=objekttype
        )

        assert expected_relation == actual_relation

    def test_build_relation_builds_correct_relation_with_urn_value(self):
        virkning = "VIRKNING"
        objekttype = "OBJEKTTYPE"

        value = "urn:urnvalue"

        expected_relation = {
            "virkning": virkning,
            "objekttype": objekttype,
            "urn": value,
        }

        actual_relation = utils.build_relation(
            value=value, virkning=virkning, objekttype=objekttype
        )

        assert expected_relation == actual_relation

    def test_build_relation_raises_ValueError_on_non_uuid_or_non_urn_value(self):
        value = "not urn or uuid"

        with pytest.raises(ValueError):
            utils.build_relation(value)

    def test_split_param_splits_on_colon(self):
        # Arrange
        value = "first:second"
        expected_result = ("first", "second")

        # Act
        actual_result = utils.split_param(value)

        # Assert
        assert expected_result == actual_result

    def test_split_param_handles_valueerror(self):
        # Arrange
        value = "nosplit"
        expected_result = ("nosplit", None)

        # Act
        actual_result = utils.split_param(value)

        # Assert
        assert expected_result == actual_result

    def test_to_lower_param_lowers_first_item(self):
        # Arrange
        value = "FIRST:second"
        expected_result = "first:second"

        # Act
        actual_result = utils.to_lower_param(value)

        # Assert
        assert expected_result == actual_result

    def test_to_lower_param_handles_value_error(self):
        # Arrange
        value = "Nosplit"
        expected_result = "nosplit"

        # Act
        actual_result = utils.to_lower_param(value)

        # Assert
        assert expected_result == actual_result

    def test_dict_from_dot_notation(self):
        # Arrange
        notation = "a.b.c"
        value = 1
        expected_result = {"a": {"b": {"c": 1}}}

        # Act
        actual_result = utils.dict_from_dot_notation(notation, value)

        # Assert
        assert expected_result == actual_result

    def test_add_journal_post_relation_fields_journalpostkode(self):
        # Arrange
        param = "journalpostkode"
        values = ["value_with_underscores", "value"]
        relation = {"testkey": "testvalue"}

        expected_result = {
            "testkey": "testvalue",
            "journalpost": [
                {"virkning": None, "journalpostkode": "value_with_underscores"},
                {"virkning": None, "journalpostkode": "value"},
            ],
        }

        # Act
        utils.add_journal_post_relation_fields(param, values, relation)

        # Assert
        assert expected_result == relation

    def test_add_journal_post_relation_fields_non_journalpostkode(self):
        # Arrange
        param = "journaldokument.dokumenttitel"
        values = ["value_with_underscores", "value"]
        relation = {"testkey": "testvalue"}

        expected_result = {
            "testkey": "testvalue",
            "journalpost": [
                {
                    "journaldokument": {"dokumenttitel": r"value\_with\_underscores"},
                    "virkning": None,
                },
                {
                    "journaldokument": {"dokumenttitel": "value"},
                    "virkning": None,
                },
            ],
        }

        # Act
        utils.add_journal_post_relation_fields(param, values, relation)

        # Assert
        assert expected_result == relation

    def test_add_journal_post_relation_fields_unknown_param(self):
        # Arrange
        param = "testparam"
        values = ["value_with_underscores", "value"]
        relation = {"testkey": "testvalue"}

        expected_result = {"testkey": "testvalue"}

        # Act
        utils.add_journal_post_relation_fields(param, values, relation)

        # Assert
        assert expected_result == relation

    @patch("oio_rest.utils.get_relation_names", new=MagicMock())
    @patch("oio_rest.utils.get_state_names", new=MagicMock())
    @patch("oio_rest.utils.get_attribute_fields")
    @patch("oio_rest.utils.get_attribute_names")
    def test_build_registration_attributes(
        self, mock_get_attribute_names, mock_get_attribute_fields
    ):
        # type: (MagicMock, MagicMock) -> None
        # Arrange
        mock_get_attribute_names.return_value = ["attributename"]
        mock_get_attribute_fields.return_value = ["arg1"]

        classname = "class"
        list_args = {
            "arg1": ["val1"],
            "arg2": ["val2"],
        }
        expected_result = {
            "attributes": {"attributename": [{"virkning": None, "arg1": "val1"}]},
            "states": {},
            "relations": {},
        }

        # Act
        actual_result = utils.build_registration(classname, list_args)

        # Assert
        assert expected_result == actual_result

    @patch("oio_rest.utils.get_relation_names", new=MagicMock())
    @patch("oio_rest.utils.get_state_names")
    @patch("oio_rest.utils.get_attribute_fields", new=MagicMock())
    @patch("oio_rest.utils.get_attribute_names", new=MagicMock())
    def test_build_registration_states(self, mock_get_state_names):
        # type: (MagicMock, MagicMock) -> None
        # Arrange
        mock_get_state_names.return_value = ["statename"]

        classname = "class"
        list_args = {
            "statename": ["val1", "val2"],
            "whatever": ["whatever"],
        }

        expected_result = {
            "states": {
                "statename": [
                    {"virkning": None, "statename": "val1"},
                    {"virkning": None, "statename": "val2"},
                ]
            },
            "attributes": {},
            "relations": {},
        }

        # Act
        actual_result = utils.build_registration(classname, list_args)

        # Assert
        assert expected_result == actual_result

    @patch("oio_rest.utils.get_relation_names")
    @patch("oio_rest.utils.get_state_names", new=MagicMock())
    @patch("oio_rest.utils.get_attribute_fields", new=MagicMock())
    @patch("oio_rest.utils.get_attribute_names", new=MagicMock())
    def test_build_registration_relations(self, mock_get_relation_names):
        # type: (MagicMock) -> None
        # Arrange
        mock_get_relation_names.return_value = ["relationname"]

        classname = "class"
        list_args = {
            "arg1": ["val1"],
            "relationname:objtype": ["urn:123"],
        }
        expected_result = {
            "relations": {
                "relationname": [
                    {"objekttype": "objtype", "urn": "urn:123", "virkning": None}
                ]
            },
            "states": {},
            "attributes": {},
        }

        # Act
        actual_result = utils.build_registration(classname, list_args)

        # Assert
        assert expected_result == actual_result
