# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
""" "Encapsulate details about the database structure."""

from collections import namedtuple

from psycopg import adapters
from psycopg.adapt import RecursiveDumper
from psycopg.pq import Format
from psycopg.types.range import TimestamptzRange

from oio_rest.db import db_structure

_attribute_fields = {}


def get_attribute_fields(attribute_name):
    """Return the field names from the PostgreSQL type in question."""

    if not _attribute_fields:
        # Initialize attr fields for ease of use.
        for c, fs in db_structure.REAL_DB_STRUCTURE.items():
            for a, v in fs["attributter"].items():
                _attribute_fields[c + a] = v + ["virkning"]

    return _attribute_fields[attribute_name.lower()]


def get_field_type(attribute_name, field_name):
    for c, fs in db_structure.REAL_DB_STRUCTURE.items():
        if "attributter_metadata" in fs:
            for a, fs in fs["attributter_metadata"].items():
                if attribute_name == c + a:
                    if field_name in fs and "type" in fs[field_name]:
                        return fs[field_name]["type"]
    return "text"


_attribute_names = {}


def get_attribute_names(class_name):
    "Return the list of all recognized attributes for this class."
    if not _attribute_names:
        for c, fs in db_structure.REAL_DB_STRUCTURE.items():
            # unfortunately, the ordering of attribute names is of
            # semantic importance to the database code, and the
            # ordering isn't consistent in Python 3.5
            #
            # specifically, the two state types of 'aktivitet' can
            # trigger occasional errors
            _attribute_names[c] = sorted(c + a for a in fs["attributter"])
    return _attribute_names[class_name.lower()]


def get_state_names(class_name):
    "Return the list of all recognized states for this class."
    states = db_structure.REAL_DB_STRUCTURE[class_name.lower()]["tilstande"]

    if isinstance(states, list):
        return [state[0] for state in states]  # pragma: no cover
    return list(states)


_relation_names = {}


def get_relation_names(class_name):
    "Return the list of all recognized relations for this class."
    if not _relation_names:
        for c, fs in db_structure.REAL_DB_STRUCTURE.items():
            _relation_names[c] = (
                fs["relationer_nul_til_en"] + fs["relationer_nul_til_mange"]
            )
    return _relation_names[class_name.lower()]


# Helper classers for adapting special types
Soegeord = namedtuple("KlasseSoegeordType", "identifier description category")
OffentlighedUndtaget = namedtuple("OffentlighedUndtagetType", "alternativtitel hjemmel")


def to_bool(s):  # pragma: no cover
    """Convert string to boolean. Passes through bool and None values."""
    if isinstance(s, bool):
        return s
    elif s is None:
        return None
    elif s in ("True", "true", "1"):
        return True
    elif s in ("False", "false", "0"):
        return False
    raise ValueError("%s is not a valid boolean value" % s)


class Virkning(namedtuple("Virkning", "timeperiod aktoerref aktoertypekode notetekst")):
    @classmethod
    def input(cls, i):  # pragma: no cover
        if i is None:
            return None
        return cls(
            TimestamptzRange(i.get("from", None), i.get("to", None)),
            i.get("aktoerref", None),
            i.get("aktoertypekode", None),
            i.get("notetekst", None),
        )


class NamedTupleDumper(RecursiveDumper):
    format = Format.BINARY

    def dump(self, obj) -> bytes:  # pragma: no cover
        values = list(map(self._tx.as_literal, obj))
        return (
            b"ROW("
            + b",".join(values)
            + b") :: "
            + obj.__class__.__name__.encode("ascii")
        )


adapters.register_dumper(Virkning, NamedTupleDumper)
adapters.register_dumper(Soegeord, NamedTupleDumper)
adapters.register_dumper(OffentlighedUndtaget, NamedTupleDumper)
