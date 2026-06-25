# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import uuid

from oio_rest.db.db_helpers import get_attribute_fields
from oio_rest.db.db_helpers import get_attribute_names
from oio_rest.db.db_helpers import get_relation_names
from oio_rest.db.db_helpers import get_state_names


def is_urn(s):
    """Return whether string is likely a URN."""
    return s.startswith("urn:") or s.startswith("URN:")


def is_uuid(s):
    """Return whether the string is a UUID (and not a URN)"""
    if not is_urn(s):
        try:
            uuid.UUID(s)
            return True
        except ValueError:  # pragma: no cover
            return False


def escape_underscores(s):
    """Return the string with underscores escaped by backslashes."""
    if s is None:
        return None  # pragma: no cover
    return s.replace("_", r"\_")


def build_relation(value, objekttype=None, virkning=None):
    relation = {"virkning": virkning, "objekttype": objekttype}
    if is_uuid(value):
        relation["uuid"] = value
    elif is_urn(value):
        relation["urn"] = value
    else:
        raise ValueError(
            "Relation has an invalid value (not a UUID or URN) '%s'" % value
        )  # pragma: no cover
    return relation


def split_param(value):
    """Return a tuple of the first and second item in a colon-separated str.

    E.g. if the input is "a:b", returns ("a", "b").
    If the input does not contain a color, e.g. "a", then ("a", None) is
    returned.
    """
    try:
        a, b = value.split(":")
        return a, b  # pragma: no cover
    except ValueError:
        return value, None


def to_lower_param(s: str) -> str:
    """Return the colon-separated string with the first
    item in lowercase. The second item is left untouched."""
    try:
        a, b = s.split(":")
        return f"{a.lower()}:{b}"  # pragma: no cover
    except ValueError:
        return s.lower()


def build_registration(class_name, list_args):
    registration = {}
    for f in list_args:
        attr = registration.setdefault("attributes", {})
        for attr_name in get_attribute_names(class_name):
            if f in get_attribute_fields(attr_name):
                for attr_value in list_args[f]:
                    attr_period = {f: escape_underscores(attr_value), "virkning": None}
                    attr.setdefault(attr_name, []).append(attr_period)

        state = registration.setdefault("states", {})
        for state_name in get_state_names(class_name):
            state_periods = state.setdefault(state_name, [])
            if f == state_name:
                for state_value in list_args[f]:
                    state_periods.append({state_name: state_value, "virkning": None})

        relation = registration.setdefault("relations", {})
        rel_name, objekttype = split_param(f)
        if rel_name in get_relation_names(class_name):
            relation.setdefault(rel_name, [])

            # Support multiple relation references at a time
            for rel in list_args[f]:
                relation[rel_name].append(build_relation(rel, objekttype))

    return registration
