# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json


def sort_inner_lists(obj):
    """Sort all inner lists and tuples by their JSON string value,
    recursively. This is quite stupid and slow, but works!

    This is purely to help comparison tests, as we don't care
    about the list ordering

    """
    if isinstance(obj, dict):
        return {k: sort_inner_lists(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return sorted(
            map(sort_inner_lists, obj),
            key=(lambda p: json.dumps(p, sort_keys=True)),
        )
    return obj


def assert_registrations_equal(expected, actual, message=None) -> None:
    # drop lora-generated timestamps & users
    for k in "fratidspunkt", "tiltidspunkt", "brugerref":
        expected.pop(k, None)
        actual.pop(k, None)

    actual = sort_inner_lists(actual)
    expected = sort_inner_lists(expected)

    # Sort all inner lists and compare
    assert expected == actual, message
