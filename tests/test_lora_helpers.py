# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from mora.lora import ParameterValuesExtractor
from mora.lora import group_params
from parameterized import parameterized


class TestLoraGroupParams:
    def test_group_params(self):
        actual = group_params(
            param_keys=("a", "b"),
            params_list=[
                (frozenset({1}), frozenset({11})),
                (frozenset({2}), frozenset({22, 33})),
                (frozenset({3}), frozenset({33})),
            ],
        )
        expected = {
            "a": {1, 2, 3},
            "b": {11, 22, 33},
        }
        assert actual == expected


class TestLoraParameterValuesExtractor:
    def test_traverse(self):
        d = {
            "a": {
                "b": 1,
                "c": "w",
                "d": ["xy", True],
                "e": {
                    "f": 2,
                    "g": [3],
                },
            },
            "b": [
                {
                    "h": 4,
                },
                5,
                "z",
                False,
            ],
            "c": {},
        }
        expected = [
            (("a", "b"), 1),
            (("a", "c"), "w"),
            (("a", "d", 0), "xy"),
            (("a", "d", 1), True),
            (("a", "e", "f"), 2),
            (("a", "e", "g", 0), 3),
            (("b", 0, "h"), 4),
            (("b", 1), 5),
            (("b", 2), "z"),
            (("b", 3), False),
        ]
        actual = ParameterValuesExtractor.traverse(d.items())
        assert list(actual) == expected

    @parameterized.expand(
        [
            (["a", "b", "c"], "c"),
            (["a", 2, "c"], "c"),
            (["id"], "uuid"),
            (["relationer", "b", "uuid"], "b"),
            (["relationer", "b", "id"], "b"),
            (["a", "relationer", "b", 3, "id"], "b"),
        ]
    )
    def test_get_key_for_path(self, path, expected):
        assert ParameterValuesExtractor.get_key_for_path(path) == expected

    def test_get_key_value_items(self):
        d = {
            "a": 1,
            "b": 2,
            "c": 3,
            "d": {
                "e": 4,
            },
        }
        search_keys = {"a", "b", "e"}
        expected = [
            ("a", 1),
            ("b", 2),
            ("e", 4),
        ]
        actual = ParameterValuesExtractor.get_key_value_items(d, search_keys)
        assert list(actual) == expected
