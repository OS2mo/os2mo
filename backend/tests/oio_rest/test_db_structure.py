# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import patch

import pytest
from oio_rest.db import db_structure


class TestDBStructure:
    def test_merge_lists(self) -> None:
        a = [1, 2, 3, 4]
        b = [4, 5, 6, 7]

        expected = [1, 2, 3, 4, 5, 6, 7]

        actual = db_structure._merge_lists(a, b)

        assert expected == actual

    def test_merge_lists_one_empty(self) -> None:
        a = [1, 2, 3, 4]
        b = []

        expected = [1, 2, 3, 4]

        actual = db_structure._merge_lists(a, b)

        assert expected == actual

    def test_merge_lists_both_empty(self) -> None:
        a = []
        b = []

        expected = []

        actual = db_structure._merge_lists(a, b)

        assert expected == actual

    def test_merge_dicts(self) -> None:
        a = {"outer1": 123, "outer2": {"inner1": ["hest"]}, "outer3": [4, 5, 6]}
        b = {"outer2": {"inner2": 1234}, "outer3": [1, 2, 3], "outer4": 456}

        expected = {
            "outer1": 123,
            "outer2": {"inner1": ["hest"], "inner2": 1234},
            "outer3": [1, 2, 3, 4, 5, 6],
            "outer4": 456,
        }

        actual = db_structure._merge_dicts(a, b)

        assert expected == actual

    def test_merge_dicts_a_is_none(self) -> None:
        a = None
        b = {"test": "hest"}

        expected = b

        actual = db_structure._merge_dicts(a, b)

        assert expected == actual

    def test_merge_dicts_b_is_none(self) -> None:
        a = {"test": "hest"}
        b = None

        expected = a

        actual = db_structure._merge_dicts(a, b)

        assert expected == actual

    @patch("oio_rest.db.db_structure._merge_dicts")
    def test_merge_objects_dicts(self, mock) -> None:
        a = {"test": 123}
        b = {"hest": 456}

        db_structure.merge_objects(a, b)

        mock.assert_called_with(a, b)

    @patch("oio_rest.db.db_structure._merge_lists")
    def test_merge_objects_lists(self, mock) -> None:
        a = [1, 2, 3]
        b = [4, 5, 6]

        db_structure.merge_objects(a, b)

        mock.assert_called_with(a, b)

    def test_merge_objects_fails_on_different_arg_types(self) -> None:
        a = [1, 2, 3]
        b = {}

        with pytest.raises(AssertionError):
            db_structure.merge_objects(a, b)

    def test_merge_objects_fails_on_unsupported_types(self) -> None:
        a = 123
        b = 456

        with pytest.raises(AttributeError):
            db_structure.merge_objects(a, b)
