# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from mora.audit import audit_log
from mora.db import get_session
from more_itertools import flatten
from oio_rest.db import Livscyklus
from oio_rest.db import to_bool
from oio_rest.db.quick_query.registration_parsing import VIRKNING
from oio_rest.db.quick_query.registration_parsing import Attribute
from oio_rest.db.quick_query.registration_parsing import Relation
from oio_rest.db.quick_query.registration_parsing import State
from oio_rest.db.quick_query.registration_parsing import ValueType
from sqlalchemy import text

RELATION = "relation"
REG = "registrering"

INFINITY = "infinity"
NINFINITY = "-infinity"


@dataclass
class InfiniteDatetime:
    value: str

    @classmethod
    def from_datetime(cls, value: datetime) -> "InfiniteDatetime":
        return cls(value.isoformat())

    @classmethod
    def from_date_string(cls, value: str) -> "InfiniteDatetime":
        """
        allows infinity or isoformat
        :param value:
        :return:
        """
        if value in (NINFINITY, INFINITY):
            return cls(value=value)

        # ensure valid and consistent format
        return cls(value=datetime.fromisoformat(value).isoformat())

    def __lt__(self, other) -> bool:
        if not isinstance(other, InfiniteDatetime):
            raise TypeError(f"unexpected type {type(other)}")
        if other.value == INFINITY:
            if self.value != INFINITY:
                return True
            else:
                raise ValueError(
                    f"unable to compare 2 infinities: self={self}, other={other}"
                )

        if other.value == NINFINITY:
            if self.value != NINFINITY:
                return False
            else:
                raise ValueError(
                    f"unable to compare 2 infinities: self={self}, other={other}"
                )

        # other is not infinity or -infinity
        if self.value == INFINITY:
            return False
        if self.value == NINFINITY:
            return True

        # both at finite
        return datetime.fromisoformat(self.value) < datetime.fromisoformat(other.value)


@dataclass(frozen=True)
class JoinTable:
    name: str
    alias: str | None = None

    @property
    def ref(self):
        if self.alias is not None:
            return self.alias
        return self.name


class SearchQueryBuilder:
    def __init__(
        self,
        class_name: str,
        limit: int | None,
        offset: int | None,
        virkning_fra: datetime | str,
        virkning_til: datetime | str,
        uuid: str | None = None,
        registreret_fra: datetime | str | None = None,
        registreret_til: datetime | str | None = None,
    ):
        """
        :param class_name: determines where to query
        :param virkning_fra: mandatory, applies to ALL filters added
        :param virkning_til: mandatory, applies to ALL filters added
        :param uuid: uuid of the object (as obj type is determined by class_name)
        :param registreret_fra: optional, applies to the registrations themselves
        :param registreret_til: optional, applies to the registrations themselves
        """

        if not isinstance(class_name, str):
            raise TypeError(f"unexpected type={type(class_name)}, value={uuid}")
        if not (uuid is None or isinstance(uuid, str)):
            raise TypeError(f"unexpected type={type(uuid)}, value={uuid}")

        self.__class_name = class_name
        self.__limit = limit
        self.__offset = offset
        self.__uuid = uuid

        # virkning
        self.__virkning_fra, self.__virkning_til = self.__validate_ts_range(
            virkning_fra, virkning_til
        )

        # core-containers
        self.__conditions: list[str] = []
        self.__relation_conditions: dict[str, list[str]] = defaultdict(list)
        self.__inner_join_tables: list[JoinTable] = []

        # eagerly create statement-parts
        self.__reg_table = f"{self.__class_name}_{REG}"
        self.__main_col = f"{self.__reg_table}.{class_name}_id"
        self.__id_col_name = "id"
        self.__count_col_name = "count"

        if self.__uuid is not None:
            self.__conditions.append(
                f"{self.__reg_table}.{self.__class_name}_id = '{self.__uuid}'"
            )

        # registreret
        self.__handle_registreret_dates(registreret_fra, registreret_til)

    @staticmethod
    def __validate_ts_range(
        start: datetime | str, end: datetime | str
    ) -> tuple[InfiniteDatetime, InfiniteDatetime]:
        """
        a defensive (type) validation and conversion
        :param start: (candidate) start of range
        :param end: (candidate) end of range
        :return:
        """
        for tmp in (start, end):
            if not isinstance(tmp, (datetime, str)):
                raise TypeError(
                    f"expected {datetime} or str, got type={type(tmp)} of value={tmp}"
                )

        if isinstance(start, str):
            start = InfiniteDatetime.from_date_string(start)
        else:
            start = InfiniteDatetime.from_datetime(start)

        if isinstance(end, str):
            end = InfiniteDatetime.from_date_string(end)
        else:
            end = InfiniteDatetime.from_datetime(end)

        if not start < end:  # NOTE: STRICT in-equality is important
            raise ValueError(
                f"start must be smaller than end, got:  start={start}, end={end}"
            )

        return start, end

    @staticmethod
    def __overlap_condition_from_range(
        fully_qualifying_var_name: str, start: InfiniteDatetime, end: InfiniteDatetime
    ) -> str:
        """
        convenient wrapper to produce a postgresql tstzrange overlap-statement

        :param fully_qualifying_var_name: postgresql name_of_table."everything_after",
        ie column + custom-type things
        :param start: start of range
        :param end: end of range
        :return: postgresql condition, suitable to put in a WHERE-clause
        """
        return (
            f"{fully_qualifying_var_name} && "
            f"tstzrange('{start.value}'::timestamptz, "
            f"'{end.value}'::timestamptz)"
        )

    def __handle_registreret_dates(
        self,
        reg_start: str | datetime | None,
        reg_end: str | datetime | None,
    ):
        """
        validate, and optionally add conditions
        :param reg_start:
        :param reg_end:
        :return:
        """
        no_start = reg_start is None
        no_end = reg_end is None
        if no_start ^ no_end:  # XOR
            # TODO: Determine old behaviour and replicate it, maybe just:
            # if reg_start is None:
            #     reg_start = NINFINITY
            # if reg_end is None:
            #     reg_end = INFINITY
            raise NotImplementedError(
                f"unexpected missing registreret date: "
                f"registreret_start={reg_start}, "
                f"registreret_end={reg_end}"
            )

        col_and_var = f"({self.__reg_table}.{REG}).timeperiod"
        if no_start and no_end:  # no reg requirements, so get will get CURRENT
            self.__conditions.append(f"upper({col_and_var})='infinity'::timestamptz")
            return  # stop early

        reg_start, reg_end = self.__validate_ts_range(reg_start, reg_end)

        # we've got both start and end as datetime
        self.__conditions.append(
            self.__overlap_condition_from_range(
                fully_qualifying_var_name=col_and_var, start=reg_start, end=reg_end
            )
        )

    @staticmethod
    def improper_sql_escape(value: str) -> str:
        """
        Improperly escape a string for direct insertion into SQL queries.

        :param value: The string to be escaped.
        :return: "Escaped" string.
        """
        return value.replace("'", "''").replace("\0", "").replace(":", "\\:")

    @classmethod
    def __postgres_comparison_from_typed_value(
        cls, value: str, type_: ValueType
    ) -> str:
        """
        determines how to convert from a python string with a postgres type to an actual
        postgres statement
        :param value: The value to be compared (as a python string)
        :param type_: The postgres type
        :return: valid postgres of the form '[comparison-operator] [value]'
        """
        # Ideally, we'd use a different query parameter key for these queries - such as
        # '&bvn~=foo' - but unfortunately such keys are hard-coded in a LOT of
        # different places throughout the code. For this reason, it is easier to
        # extract the sentinel from the VALUE at this point in time.
        use_is_similar_sentinel = "|LORA-PLEASE-USE-IS-SIMILAR|"
        if value.startswith(use_is_similar_sentinel):
            value = value[len(use_is_similar_sentinel) :]
            return f"similar to '{cls.improper_sql_escape(value)}'"
        if type_ is ValueType.TEXT:
            # always uses case insensitive matching
            return f"ilike '{cls.improper_sql_escape(value)}'"
        if type_ is ValueType.BOOL:
            parsed_bool = to_bool(value)
            if parsed_bool is None:
                raise ValueError(f"unexpected value {value}")
            return "= " + ("TRUE" if parsed_bool else "FALSE")

        raise Exception(f"unexpected type_: {type_}, with associated value {value}")

    def add_attribute(self, attr: Attribute):
        """
        adds a filter to the query (in WHERE-clause, solely 'AND'-filtering)
        internally inner-joins tables as needed
        :param attr: the attribute object specifying a filter
        :return:
        """
        table_name = "_".join([self.__class_name, "attr", attr.type])
        join_table = JoinTable(name=table_name)
        if join_table not in self.__inner_join_tables:
            self.__inner_join_tables.append(join_table)

        comparison = self.__postgres_comparison_from_typed_value(
            value=attr.value, type_=attr.value_type
        )
        self.__conditions.append(f"{join_table.ref}.{attr.key} {comparison}")

    def add_state(self, state: State):
        """
        adds a filter to the query (in WHERE-clause, solely 'AND'-filtering)
        internally inner-joins tables as needed

        :param state: the state object specifying a filter
        :return:
        """
        table_name = "_".join([self.__class_name, "tils", state.key])
        join_table = JoinTable(name=table_name)
        if join_table not in self.__inner_join_tables:
            self.__inner_join_tables.append(join_table)
        self.__conditions.append(f"{join_table.ref}.{state.key} = '{state.value}'")

    def add_relation(self, relation: Relation):
        """
        adds a filter to the query (in WHERE-clause, solely 'AND'-filtering)
        internally inner-joins tables as needed

        :param relation: the relation object specifying a filter
        :return:
        """
        table_name = f"{self.__class_name}_{RELATION}"
        table_alias = f"{table_name}_{relation.type}"
        join_table = JoinTable(name=table_name, alias=table_alias)
        if join_table not in self.__inner_join_tables:
            self.__inner_join_tables.append(join_table)
        # HACK: This is a hack implemented to support checking for vacant managers.
        #       Vacant managers are encoded in two ways, either:
        #       * As a tilknyttedebrugere row with nulls in both UUID and URN, or
        #       * A missing tilknyttedebrugere row
        #       Depending on whether other validities exist within the same registration.
        #
        #       The logic here however should be useful for other emptiness checks.
        #
        #       In the future this should be implemented without hacks, but so far
        #       this is unfortunately the easiest way to expand LoRa.
        #
        #       There is similar implementation to this for: LORA-PLEASE-USE-IS-SIMILAR
        if relation.id == "urn:LORA-PLEASE-FIND-NULL-UUID-AND-URN":
            # This handles the case where a row exists, but has double nulls
            # This situation occurs multiple validities exist, where one is vacant
            base_condition = f"{join_table.ref}.rel_type = '{relation.type}'"
            base_condition += f" AND {join_table.ref}.rel_maal_uuid is null"
            base_condition += f" AND {join_table.ref}.rel_maal_urn is null"

            # This handles the case where no row exists
            # This situation occurs when a vacant manager is created as the sole validity
            # This constructs a validity filter for our subquery, ensuring that the rows
            # we search for have the same validity as the rest of the query.
            virkning_filter = self.__overlap_condition_from_range(
                fully_qualifying_var_name=f"(r.{VIRKNING}).timeperiod",
                start=self.__virkning_fra,
                end=self.__virkning_til,
            )
            # Subquery checking for relation rows of the given type in the given interval
            # within our current registration.
            no_rows_subquery = f"""
                SELECT
                    1
                FROM
                    {table_name} r
                WHERE
                    r.rel_type = '{relation.type}' AND
                    r.organisationfunktion_registrering_id = {self.__class_name}_{REG}.id AND
                    {virkning_filter}
            """
            # Either the row cannot exist OR the row must have double nulls
            base_condition = f"(NOT EXISTS({no_rows_subquery})) OR ({base_condition})"
        else:
            id_var_name = "rel_maal_uuid" if relation.id_is_uuid else "rel_maal_urn"
            base_condition = f"""{join_table.ref}.rel_type = '{relation.type}'
             AND {join_table.ref}.{id_var_name} = '{relation.id}'"""

        if relation.object_type is not None:
            obj_condition = f"{join_table.ref}.objekt_type = '{relation.object_type}'"
            condition = f"{base_condition} AND {obj_condition}"
        else:
            condition = base_condition

        self.__relation_conditions[relation.type].append("(" + condition + ")")

    def __build_subquery(self):
        """
        This is the cool query, where we actually do stuff with the DB

        :return: a valid postgresql statement (MINUS ";" at the end)
        """

        select_from_stmt = f"""
        SELECT {self.__main_col} as {self.__id_col_name}
        FROM {self.__reg_table}"""

        additional_conditions = []  # just to avoid altering state
        inner_join_stmt = ""
        if self.__inner_join_tables:  # add the tables needed
            joins = (
                f"INNER JOIN {join_table.name} {join_table.ref} ON {join_table.ref}.{self.__class_name}_{REG}_id = {self.__reg_table}.id"
                for join_table in self.__inner_join_tables
            )
            inner_join_stmt = " ".join(joins)

            # add time-related conditions to EVERY table
            for join_table in self.__inner_join_tables:
                additional_conditions.append(
                    self.__overlap_condition_from_range(
                        fully_qualifying_var_name=f"({join_table.ref}.{VIRKNING})."
                        f"timeperiod",
                        start=self.__virkning_fra,
                        end=self.__virkning_til,
                    )
                )

        # build the WHERE statement, as it will be non-empty
        deleted_cycle_code = f"'{Livscyklus.SLETTET.value}'::livscykluskode"
        used_conditions = [  # don't include deleted in search
            f"({self.__reg_table}.{REG}).livscykluskode != {deleted_cycle_code}"
        ]

        if self.__conditions:
            used_conditions += self.__conditions

        if additional_conditions:
            used_conditions += additional_conditions

        if self.__relation_conditions:
            for conditions in self.__relation_conditions.values():
                used_conditions.append(" (" + " OR ".join(conditions) + ")")

        where_stmt = "WHERE " + " AND ".join(used_conditions)

        return f"{select_from_stmt} {inner_join_stmt} {where_stmt}"

    def get_query(self) -> str:
        """
        Get a query reflecting the currently added constraints.
        Does not alter state of this object

        :return: a valid postgresql statement
        """
        select_from_stmt = self.__build_subquery()
        order_by_stmt = f"ORDER BY {self.__id_col_name}"
        limit_stmt = f"LIMIT {self.__limit}" if self.__limit is not None else ""
        offset_stmt = f"OFFSET {self.__offset}" if self.__offset is not None else ""

        return f"{select_from_stmt} {order_by_stmt} {limit_stmt} {offset_stmt};"


def ensure_uuid(uuid: UUID | str) -> UUID:
    if isinstance(uuid, UUID):
        return uuid
    return UUID(uuid)


async def quick_search(
    class_name: str,
    uuid: str | UUID | None,
    registration: dict,
    virkning_fra: datetime | str,
    virkning_til: datetime | str,
    registreret_fra: datetime | str | None = None,
    registreret_til: datetime | str | None = None,
    life_cycle_code=None,
    user_ref=None,
    note=None,
    any_attr_value_arr=None,
    any_rel_uuid_arr=None,
    first_result=None,
    max_results=None,
) -> tuple[list[str]]:
    """
    (partial) Implementation of MOX search api against LoRa.
    Returns results (uuids) from LoRa.

    :param class_name: Determines LoRa object type (NotImplemented for every classes)
    :param uuid:
    :param registration:
    :param virkning_fra:
    :param virkning_til:
    :param registreret_fra:
    :param registreret_til:
    :param life_cycle_code: NotImplemented
    :param user_ref: NotImplemented
    :param note: NotImplemented
    :param any_attr_value_arr: NotImplemented
    :param any_rel_uuid_arr: NotImplemented
    :param first_result:
    :param max_results:
    :return: Tuple of 1, containing list of uuids
    """

    # Parse input
    org_class_name = class_name
    class_name = class_name.lower()
    if class_name not in (
        "organisationfunktion",
        "organisationenhed",
        "facet",
        "bruger",
        "klasse",
        "itsystem",
    ):
        raise NotImplementedError(f"not implemented for {class_name}")

    # Non-implemented search parameters
    if life_cycle_code is not None:
        raise NotImplementedError(
            f"life_cycle_code not implemented. Received value={life_cycle_code}"
        )
    if user_ref is not None:
        raise NotImplementedError(
            f"user_ref not implemented. Received value={user_ref}"
        )
    if note is not None:
        raise NotImplementedError(f"note not implemented. Received value={note}")
    if any_attr_value_arr is not None:
        raise NotImplementedError(
            f"any_attr_value_arr not implemented. Received value={any_attr_value_arr}"
        )
    if any_rel_uuid_arr is not None:
        raise NotImplementedError(
            f"any_rel_uuid_arr not implemented. Received value={any_rel_uuid_arr}"
        )

    # parse registration
    attributes = Attribute.parse_registration_attributes(
        class_name=class_name, attributes=registration["attributes"]
    )
    states = State.parse_registration_states(
        class_name=class_name, states=registration["states"]
    )
    relations = Relation.parse_registration_relations(
        class_name=class_name, relations=registration["relations"]
    )

    if uuid is not None:
        uuid = str(uuid)

    # build query
    qb = SearchQueryBuilder(
        class_name=class_name,
        limit=max_results,
        offset=first_result,
        virkning_fra=virkning_fra,
        virkning_til=virkning_til,
        uuid=uuid,
        registreret_fra=registreret_fra,
        registreret_til=registreret_til,
    )

    for x in attributes:
        qb.add_attribute(x)
    for x in states:
        qb.add_state(x)
    for x in relations:
        qb.add_relation(x)

    sql = text(qb.get_query())
    audit_log_arguments = {
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
    result = await session.execute(sql)
    output = result.fetchall()
    uuids = list(flatten(output))
    audit_log(
        session,
        "quick_search",
        org_class_name,
        audit_log_arguments,
        list(map(ensure_uuid, uuids)),
    )

    return (uuids,)  # explicit tuple
