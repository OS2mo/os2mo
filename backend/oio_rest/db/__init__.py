# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import collections
import copy
import datetime
import enum
import functools
import pathlib
from contextlib import suppress
from typing import Any
from uuid import UUID

import dateutil
import sqlalchemy
from dateutil import parser as date_parser
from jinja2 import Environment
from jinja2 import FileSystemLoader
from mora.audit import audit_log
from mora.auth.middleware import get_authenticated_user
from mora.db import get_session
from more_itertools import one
from psycopg import sql
from psycopg.adapt import Transformer
from psycopg.types.range import TimestamptzRange
from ramodels.base import to_parsable_timestamp
from sqlalchemy import text
from sqlalchemy.exc import StatementError

from ..custom_exceptions import BadRequestException
from ..custom_exceptions import DBException
from ..custom_exceptions import NotFoundException
from .db_helpers import AktoerAttr
from .db_helpers import DokumentVariantType
from .db_helpers import JournalDokument
from .db_helpers import JournalNotat
from .db_helpers import OffentlighedUndtaget
from .db_helpers import Soegeord
from .db_helpers import VaerdiRelationAttr
from .db_helpers import get_attribute_fields
from .db_helpers import get_attribute_names
from .db_helpers import get_field_type
from .db_helpers import get_relation_field_type
from .db_helpers import get_state_names
from .db_helpers import to_bool

"""
    Jinja2 Environment
"""

jinja_env = Environment(
    loader=FileSystemLoader(
        str(pathlib.Path(__file__).parent / "sql" / "invocations" / "templates"),
    )
)

transformer = Transformer(None)


def adapt(value):
    literal = transformer.as_literal(value)
    string = str(literal, encoding="utf-8")
    # The SQL templates return statements ready to be executed as-is but SQLAlchemy
    # insists on binding parameters (':myparam') before execution. This won't work
    # until we get rid of templating, and do everything properly in SQLAlchemy,
    # so we have to escape colons before returning the templated statement.
    escaped = string.replace(":", "\\:")
    return escaped


jinja_env.filters["adapt"] = adapt


#
# GENERAL FUNCTION AND CLASS DEFINITIONS
#


def convert_attr_value(attribute_name, attribute_field_name, attribute_field_value):
    # For simple types that can be adapted by standard psycopg2 adapters, just
    # pass on. For complex types like "Soegeord" with specialized adapters,
    # convert to the class for which the adapter is registered.
    field_type = get_field_type(attribute_name, attribute_field_name)
    if field_type == "soegeord":
        return [Soegeord(*ord) for ord in attribute_field_value]
    elif field_type == "offentlighedundtagettype":  # pragma: no cover
        if (
            "alternativtitel" not in attribute_field_value
            and "hjemmel" not in attribute_field_value
        ):
            # Empty object, so provide the DB with a NULL, so that the old
            # value is not overwritten.
            return None
        else:
            return OffentlighedUndtaget(
                attribute_field_value.get("alternativtitel", None),
                attribute_field_value.get("hjemmel", None),
            )
    elif field_type == "date":  # pragma: no cover
        return datetime.datetime.strptime(
            attribute_field_value,
            "%Y-%m-%d",
        ).date()
    elif field_type == "timestamptz":  # pragma: no cover
        return date_parser.parse(attribute_field_value)
    elif field_type == "interval(0)":  # pragma: no cover
        # delegate actual interval parsing to PostgreSQL in all cases,
        # bypassing psycopg2 cleverness
        s = sql.quote(attribute_field_value or "0")
        return sql.Literal(f"{s} :: interval")
    elif field_type == "boolean":  # pragma: no cover
        return to_bool(attribute_field_value)
    else:
        return attribute_field_value


def convert_relation_value(class_name, field_name, value):
    field_type = get_relation_field_type(class_name, field_name)
    if field_type == "journalnotat":  # pragma: no cover
        return JournalNotat(
            value.get("titel", None),
            value.get("notat", None),
            value.get("format", None),
        )
    elif field_type == "journaldokument":  # pragma: no cover
        ou = value.get("offentlighedundtaget", {})
        return JournalDokument(
            value.get("dokumenttitel", None),
            OffentlighedUndtaget(
                ou.get("alternativtitel", None), ou.get("hjemmel", None)
            ),
        )
    elif field_type == "aktoerattr":  # pragma: no cover
        if value:
            return AktoerAttr(
                value.get("accepteret", None),
                value.get("obligatorisk", None),
                value.get("repraesentation_uuid", None),
                value.get("repraesentation_urn", None),
            )
    elif field_type == "vaerdirelationattr":  # pragma: no cover
        result = VaerdiRelationAttr(
            value.get("forventet", None), value.get("nominelvaerdi", None)
        )
        return result
    # Default: no conversion.
    return value


def convert_attributes(attributes):
    "Convert attributes from dictionary to list in correct order."
    if attributes:
        for attr_name in attributes:
            current_attr_periods = attributes[attr_name]
            converted_attr_periods = []
            for attr_period in current_attr_periods:
                field_names = get_attribute_fields(attr_name)
                attr_value_list = [
                    convert_attr_value(attr_name, f, attr_period[f])
                    if f in attr_period
                    else None
                    for f in field_names
                ]
                converted_attr_periods.append(attr_value_list)
            attributes[attr_name] = converted_attr_periods
    return attributes


def convert_relations(relations, class_name):
    "Convert relations - i.e., convert each field according to its type"
    if relations:
        for rel_name in relations:
            periods = relations[rel_name]
            for period in periods:
                if not isinstance(period, dict):  # pragma: no cover
                    raise BadRequestException(
                        'mapping expected for "%s" in "%s" - got %r'
                        % (period, rel_name, period)
                    )
                for field in period:
                    converted = convert_relation_value(class_name, field, period[field])
                    period[field] = converted
    return relations


def convert_variants(variants):  # pragma: no cover
    """Convert variants."""
    # TODO
    if variants is None:
        return None
    return [DokumentVariantType.input(variant) for variant in variants]


class Livscyklus(enum.Enum):
    OPSTAAET = "Opstaaet"
    IMPORTERET = "Importeret"
    PASSIVERET = "Passiveret"
    SLETTET = "Slettet"
    RETTET = "Rettet"


"""
    GENERAL SQL GENERATION.

    All of these functions generate bits of SQL to use in complete statements.
    At some point, we might want to factor them to an "sql_helpers.py" module.
"""


def sql_state_array(state, periods, class_name):
    """Return an SQL array of type <state>TilsType."""
    t = jinja_env.get_template("state_array.sql")
    sql = t.render(class_name=class_name, state_name=state, state_periods=periods)
    return sql


def sql_attribute_array(attribute, periods):
    """Return an SQL array of type <attribute>AttrType[]."""
    t = jinja_env.get_template("attribute_array.sql")
    sql = t.render(attribute_name=attribute, attribute_periods=periods)
    return sql


def sql_relations_array(class_name, relations):
    """Return an SQL array of type <class_name>RelationType[]."""
    t = jinja_env.get_template("relations_array.sql")
    sql = t.render(class_name=class_name, relations=relations)
    return sql


def sql_convert_registration(registration, class_name):
    """Convert input JSON to the SQL arrays we need."""
    registration["attributes"] = convert_attributes(registration["attributes"])
    registration["relations"] = convert_relations(registration["relations"], class_name)
    if "variants" in registration:  # pragma: no cover
        registration["variants"] = adapt(convert_variants(registration["variants"]))
    states = registration["states"]
    sql_states = []
    for sn in get_state_names(class_name):
        qsn = class_name.lower() + sn  # qualified_state_name
        if qsn in states:
            periods = states[qsn]
        elif sn in states:
            periods = states[sn]
        else:
            periods = None

        sql_states.append(sql_state_array(sn, periods, class_name))
    registration["states"] = sql_states

    attributes = registration["attributes"]
    sql_attributes = []
    for a in get_attribute_names(class_name):
        periods = attributes[a] if a in attributes else None
        sql_attributes.append(sql_attribute_array(a, periods))
    registration["attributes"] = sql_attributes

    relations = registration["relations"]
    sql_relations = sql_relations_array(class_name, relations)
    # print "CLASS", class_name

    registration["relations"] = sql_relations

    return registration


def sql_get_registration(
    class_name, time_period, life_cycle_code, user_ref, note, registration
):
    """
    Return a an SQL registrering object of type
    <class_name>RegistreringType[].
    Expects a Registration object returned from sql_convert_registration.
    """
    sql_template = jinja_env.get_template("registration.sql")
    sql = sql_template.render(
        class_name=class_name,
        time_period=time_period,
        life_cycle_code=life_cycle_code,
        user_ref=user_ref,
        note=note,
        states=registration["states"],
        attributes=registration["attributes"],
        relations=registration["relations"],
        variants=registration.get("variants", None),
    )
    return sql


"""
    GENERAL OBJECT RELATED FUNCTIONS
"""


async def object_exists(class_name: str, uuid: str) -> bool:
    """Check if an object with this class name and UUID exists already."""
    sql = text(
        f"""
        SELECT EXISTS(
            SELECT 1
            FROM {class_name.lower() + "_registrering"}
            WHERE {class_name.lower() + "_id"} = :uuid
        )
        """
    )
    arguments = {"uuid": uuid}

    session = get_session()
    try:
        audit_log(session, "object_exists", class_name, arguments, [UUID(uuid)])
        result = await session.scalar(sql, arguments)
    except StatementError as e:  # pragma: no cover
        if e.orig.sqlstate is not None and e.orig.sqlstate[:2] == "MO":
            status_code = int(e.orig.sqlstate[2:])
            raise DBException(status_code, e.orig.diag.message_primary)
        else:
            raise
    assert isinstance(result, bool)
    return result


async def create_or_import_object(class_name, note, registration, uuid=None):
    """Create a new object by calling the corresponding stored procedure.

    Create a new object by calling actual_state_create_or_import_{class_name}.
    It is necessary to map the parameters to our custom PostgreSQL data types.
    """

    if uuid is None:
        life_cycle_code = Livscyklus.OPSTAAET.value
    elif await object_exists(class_name, uuid):
        life_cycle_code = Livscyklus.RETTET.value
    else:
        life_cycle_code = Livscyklus.IMPORTERET.value

    user_ref = str(get_authenticated_user())

    registration = sql_convert_registration(registration, class_name)
    sql_registration = sql_get_registration(
        class_name, None, life_cycle_code, user_ref, note, registration
    )

    sql_template = jinja_env.get_template("create_object.sql")
    sql = text(
        sql_template.render(
            class_name=class_name,
            uuid=uuid,
            life_cycle_code=life_cycle_code,
            user_ref=user_ref,
            note=note,
            registration=sql_registration,
        )
    )

    session = get_session()
    try:
        result = await session.execute(sql)
    except StatementError as e:  # pragma: no cover
        if e.orig.sqlstate is not None and e.orig.sqlstate[:2] == "MO":
            status_code = int(e.orig.sqlstate[2:])
            raise DBException(status_code, e.orig.diag.message_primary)
        else:
            raise
    return result.fetchone()[0]


async def delete_object(class_name, note, uuid):  # pragma: no cover
    """Delete object by using the stored procedure.

    Deleting is the same as updating with the life cycle code "Slettet".
    """
    if not (await object_exists(class_name, uuid)):
        raise NotFoundException(f"No {class_name} with ID {uuid} found.")

    if (await get_life_cycle_code(class_name, uuid)) == Livscyklus.SLETTET.value:
        # Already deleted, no problem as DELETE is idempotent.
        return

    await get_session().execute(
        sqlalchemy.text(
            f"SELECT _as_create_{class_name}_registrering(:uuid, 'Slettet'::livscykluskode, :actor, :note);"
        ),
        {
            "uuid": uuid,
            "actor": get_authenticated_user(),
            "note": note,
        },
    )


async def passivate_object(class_name, note, registration, uuid):
    """Passivate object by calling the stored procedure."""

    user_ref = str(get_authenticated_user())
    life_cycle_code = Livscyklus.PASSIVERET.value
    sql_template = jinja_env.get_template("update_object.sql")
    registration = sql_convert_registration(registration, class_name)
    sql = text(
        sql_template.render(
            class_name=class_name,
            uuid=uuid,
            life_cycle_code=life_cycle_code,
            user_ref=user_ref,
            note=note,
            states=registration["states"],
            attributes=registration["attributes"],
            relations=registration["relations"],
            variants=registration.get("variants", None),
        )
    )

    session = get_session()
    try:
        result = await session.execute(sql)
    except StatementError as e:  # pragma: no cover
        if e.orig.sqlstate is not None and e.orig.sqlstate[:2] == "MO":
            status_code = int(e.orig.sqlstate[2:])
            raise DBException(status_code, e.orig.diag.message_primary)
        else:
            raise
    # coverage: pause
    return result.fetchone()[0]
    # coverage: unpause


async def update_object(
    class_name, note, registration, uuid=None, life_cycle_code=Livscyklus.RETTET.value
):
    """Update object with the partial data supplied."""
    user_ref = str(get_authenticated_user())

    registration = sql_convert_registration(registration, class_name)

    sql_template = jinja_env.get_template("update_object.sql")
    sql = text(
        sql_template.render(
            class_name=class_name,
            uuid=uuid,
            life_cycle_code=life_cycle_code,
            user_ref=user_ref,
            note=note,
            states=registration["states"],
            attributes=registration["attributes"],
            relations=registration["relations"],
            variants=registration.get("variants", None),
        )
    )

    session = get_session()
    try:
        await session.execute(sql)
    except StatementError as e:  # pragma: no cover
        noop_msg = (
            "Aborted updating {} with id [{}] as the given data, "
            "does not give raise to a new registration.".format(
                class_name.lower(), uuid
            )
        )
        if e.orig.diag.message_primary.startswith(noop_msg):
            return uuid
        elif e.orig.sqlstate is not None and e.orig.sqlstate[:2] == "MO":
            status_code = int(e.orig.sqlstate[2:])
            raise DBException(status_code, e.orig.diag.message_primary)
        else:
            raise

    return uuid


async def list_and_consolidate_objects(
    class_name, uuid, virkning_fra, virkning_til, registreret_fra, registreret_til
):
    """List objects with the given uuids, consolidating the 'virkninger' and
    optionally filtering by the given virkning and registrering periods."""
    obj = await list_objects(
        class_name=class_name,
        uuid=uuid,
        virkning_fra="-infinity",
        virkning_til="infinity",
        registreret_fra=registreret_fra,
        registreret_til=registreret_til,
    )
    _consolidate_and_trim_object_virkninger(
        obj, valid_from=virkning_fra, valid_to=virkning_til
    )
    return obj


async def list_objects(
    class_name: str,
    uuid: list | None,
    virkning_fra,
    virkning_til,
    registreret_fra,
    registreret_til,
):
    """List objects with the given uuids, optionally filtering by the given
    virkning and registering periods."""
    assert isinstance(uuid, list) or not uuid

    registration_period = None
    if registreret_fra is not None or registreret_til is not None:
        registration_period = TimestamptzRange(registreret_fra, registreret_til)

    arguments = {
        "uuid": uuid,
        "registrering_tstzrange": registration_period,
        "virkning_tstzrange": TimestamptzRange(virkning_fra, virkning_til),
    }

    sql_template = jinja_env.get_template("list_objects.sql")
    sql = sql_template.render(class_name=class_name, **arguments)

    session = get_session()
    try:
        result = await session.execute(text(sql))
    except StatementError as e:
        if (
            e.orig.sqlstate is not None and e.orig.sqlstate[:2] == "MO"
        ):  # pragma: no cover
            status_code = int(e.orig.sqlstate[2:])
            raise DBException(status_code, e.orig.diag.message_primary)
        else:
            raise
    output = one(result.fetchone())
    uuids = []
    if output is not None:
        uuids = [entry["id"] for entry in output]
    audit_log(session, "list_objects", class_name, arguments, list(map(UUID, uuids)))

    ret = filter_json_output((output,))
    with suppress(IndexError):
        repair_relation_nul_til_mange(ret[0])

    return ret


def repair_relation_nul_til_mange(objects: list[dict[str, Any]]) -> None:
    """Fix 'nul_til_mange' relations.

    Args:
        objects: Objects returned from the database of the format:
            [
              {
                "id": "f06ee470-9f17-566f-acbe-e938112d46d9",
                "registreringer": [
                  {
                    ...
                    "attributter": {...},
                    "tilstande": {...},
                    "relationer": {
                      "overordnet": [
                        {
                          "virkning": {...},
                          "uuid": "3b866d97-0b1f-48e0-8078-686d96f430b3"
                        }
                      ],
                      ...
                    }
                  }
                ]
              }
            ]


    According to the schema validation in backend/oio_rest/validate.py
    :_generate_relationer(), a 'nul_til_mange' relation should have exactly one of
      - uuid (UUID)
      - urn (URN)
      - uuid (empty string) *and* urn (empty string)

    Unfortunately, these empty strings are actually saved to the database as NULLs, and
    filter_empty() removes these values from the response (although the implementation
    also filters falsy values anyway). This function ensures that the object properly
    conforms to the validation schema by changing the given argument by reference.
    """
    for obj in objects:
        for registrering in obj["registreringer"]:
            with suppress(KeyError):
                for values in registrering["relationer"].values():
                    for value in values:
                        if {"uuid", "urn"}.isdisjoint(value.keys()):
                            value["uuid"] = ""
                            value["urn"] = ""


def filter_json_output(output):
    """Filter the JSON output returned from the DB-layer."""
    if isinstance(output, dict):
        if "cleared" in output:
            # Handle clearable wrapper db-types.
            # {"blah": {"value": true, "cleared": false}} becomes simply {"blah": true}
            return output.get("value", {})

        if "timeperiod" in output:
            timeperiod = output.pop("timeperiod")
            f, t = timeperiod[1:-1].split(",")
            from_included = timeperiod[0] == "["
            to_included = timeperiod[-1] == "]"

            # Get rid of quotes
            if f[0] == '"':
                f = f[1:-1]
            if t[0] == '"':
                t = t[1:-1]

            r = {
                k: v
                for k, v in output.items()
                if v or (k == "brugervendtnoegle" and v == "")
            }
            r["from"] = f
            r["to"] = t
            r["from_included"] = from_included
            r["to_included"] = to_included
            return r

        return {
            k: v2
            for k, v in output.items()
            if (v2 := filter_json_output(v)) or (k == "brugervendtnoegle" and v == "")
        }
    elif isinstance(output, list):
        return [v2 for v in output if (v2 := filter_json_output(v))]
    elif isinstance(output, tuple):
        return tuple(v2 for v in output if (v2 := filter_json_output(v)))
    return output


def transform_relations(o):  # pragma: no cover
    """Recurse through output to transform relation lists to dicts.

    Currently, this only applies to DokumentDel relations, because the cast
    to.JSON for other types of relations is currently done in PostgreSQL cast
    functions.
    """
    if isinstance(o, dict):
        if "relationer" in o and isinstance(o["relationer"], (list, tuple)):
            relations = o["relationer"]
            rel_dict = {}
            for rel in relations:
                # Remove the reltype from the dict and add to the output dict
                rel_type = rel.pop("reltype")
                rel_dict.setdefault(rel_type, []).append(rel)
            o["relationer"] = rel_dict
            return o
        else:
            return {k: transform_relations(v) for k, v in o.items()}
    elif isinstance(o, list):
        return [transform_relations(v) for v in o]
    elif isinstance(o, tuple):
        return tuple(transform_relations(v) for v in o)
    else:
        return o


def _consolidate_and_trim_object_virkninger(
    obj, valid_from="-infinity", valid_to="infinity"
):
    """
    Read a LoRa object and consolidate multiple sequential LoRa virkning
    objects that could have been represented by one object.
    Optionally trims the resulting object removing virkninger outside the
    given interval of valid_from/valid_to

    :param obj: An object from a list-operation on the database
    """

    if not obj:
        return obj

    # Move functions to local scope. Feels silly, but they are called a lot.
    consolidate_virkninger = _consolidate_virkninger
    trim_virkninger = _trim_virkninger

    for result in obj[0]:
        registration = result["registreringer"][0]
        for category_key in ("attributter", "relationer", "tilstande"):
            category = registration.get(category_key)
            if not category:
                continue

            for key in list(category.keys()):
                virkninger = consolidate_virkninger(category[key])
                category[key] = trim_virkninger(virkninger, valid_from, valid_to)

                # If no virkninger are left after trimming, delete the key
                if not category[key]:
                    del category[key]

            # If the entire category is empty after trimming, delete the
            # category key
            if not registration[category_key]:
                del registration[category_key]


def _consolidate_virkninger(virkninger_list):
    """
    Consolidate a single list of LoRa virkninger.

    :param virkninger_list: A list of virkninger
    :return: A list of consolidated virkninger
    """

    if not virkninger_list:  # pragma: no cover
        return virkninger_list

    # Collect virkninger with the same values
    virkning_map = collections.defaultdict(list)
    for virkning in virkninger_list:
        virkning_copy = copy.copy(virkning)
        del virkning_copy["virkning"]
        virkning_key = tuple(virkning_copy.items())
        virkning_map[virkning_key].append(virkning)

    new_virkninger = []
    for v in virkning_map.values():
        sorted_virkninger = sorted(v, key=lambda x: x.get("virkning").get("from"))

        first = sorted_virkninger[0]
        current_virkning = first.copy()
        current_virkning["virkning"] = first["virkning"].copy()

        for next_virkning in sorted_virkninger[1:]:
            # Postgres always returns timestamps in the same format with the
            # same timezone, so a naive comparison is safe here.
            if current_virkning["virkning"]["to"] == next_virkning["virkning"]["from"]:
                current_virkning["virkning"]["to"] = next_virkning["virkning"]["to"]
            else:
                new_virkninger.append(current_virkning)
                current_virkning = next_virkning
        new_virkninger.append(current_virkning)

    return new_virkninger


@functools.lru_cache(maxsize=128)
def _parse_timestamp(timestamp: datetime.datetime | str) -> datetime.datetime:
    if timestamp == "infinity":
        dt = datetime.datetime.max
    elif timestamp == "-infinity":
        dt = datetime.datetime.min
    elif type(timestamp) is str:
        dt = dateutil.parser.isoparse(to_parsable_timestamp(timestamp))
    elif isinstance(timestamp, datetime.datetime):  # pragma: no cover
        dt = timestamp
    else:  # pragma: no cover
        raise TypeError(f"Invalid parameter {timestamp}")

    if not dt.tzinfo:
        dt = dt.replace(tzinfo=datetime.UTC)

    return dt


def _trim_virkninger(virkninger_list, valid_from, valid_to):
    """
    Trim a list of LoRa virkninger. Removes all virkninger not inside the
    given interval of valid_from/valid_to
    """
    valid_from = _parse_timestamp(valid_from)
    valid_to = _parse_timestamp(valid_to)

    def filter_fn(virkning):
        virkning_to = _parse_timestamp(virkning["virkning"]["to"])
        to_included = virkning["virkning"]["to_included"]
        if to_included and virkning_to < valid_from:  # pragma: no cover
            return False
        elif not to_included and virkning_to <= valid_from:
            return False

        virkning_from = _parse_timestamp(virkning["virkning"]["from"])
        from_included = virkning["virkning"]["from_included"]
        if from_included and valid_to < virkning_from:
            return False
        elif not from_included and valid_to <= virkning_from:  # pragma: no cover
            return False

        return True

    return list(filter(filter_fn, virkninger_list))


async def search_objects(
    class_name,
    uuid,
    registration,
    virkning_fra=None,
    virkning_til=None,
    registreret_fra=None,
    registreret_til=None,
    life_cycle_code=None,
    user_ref=None,
    note=None,
    any_attr_value_arr=None,
    any_rel_uuid_arr=None,
    first_result=0,
    max_results=2147483647,
):
    if not any_attr_value_arr:
        any_attr_value_arr = []
    if not any_rel_uuid_arr:
        any_rel_uuid_arr = []
    if uuid is not None:
        uuid = str(uuid)

    time_period = None
    if registreret_fra is not None or registreret_til is not None:  # pragma: no cover
        time_period = TimestamptzRange(registreret_fra, registreret_til)

    registration = sql_convert_registration(registration, class_name)
    sql_registration = sql_get_registration(
        class_name, time_period, life_cycle_code, user_ref, note, registration
    )

    sql_template = jinja_env.get_template("search_objects.sql")

    virkning_soeg = None
    if virkning_fra is not None or virkning_til is not None:
        virkning_soeg = TimestamptzRange(virkning_fra, virkning_til)

    sql = text(
        sql_template.render(
            first_result=first_result,
            uuid=uuid,
            class_name=class_name,
            registration=sql_registration,
            any_attr_value_arr=any_attr_value_arr,
            any_rel_uuid_arr=any_rel_uuid_arr,
            max_results=max_results,
            virkning_soeg=virkning_soeg,
        )
    )
    arguments = {
        "uuid": uuid,
        "virkning_fra": virkning_fra,
        "virkning_til": virkning_til,
        "registreret_fra": registreret_fra,
        "registreret_til": registreret_til,
        "life_cycle_code": life_cycle_code,
        "user_ref": user_ref,
        "note": note,
        "any_attr_value_arr": any_attr_value_arr,
        "any_rel_uuid_arr": any_rel_uuid_arr,
        "first_result": first_result,
        "max_results": max_results,
    }

    session = get_session()
    try:
        result = await session.execute(sql)
    except StatementError as e:  # pragma: no cover
        if e.orig.sqlstate is not None and e.orig.sqlstate[:2] == "MO":
            status_code = int(e.orig.sqlstate[2:])
            raise DBException(status_code, e.orig.diag.message_primary)
        else:
            raise
    uuids = one(result.fetchone())
    audit_log(session, "search_objects", class_name, arguments, list(map(UUID, uuids)))

    return (uuids,)


async def get_life_cycle_code(class_name, uuid):
    n = datetime.datetime.now()
    n1 = n + datetime.timedelta(seconds=1)
    regs = await list_objects(class_name, [uuid], n, n1, None, None)
    reg = regs[0][0]
    livscykluskode = reg["registreringer"][0]["livscykluskode"]

    return livscykluskode
