# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import enum
import functools
import operator
import typing
from contextlib import suppress

from os2mo_http_trigger_protocol import EventType  # noqa
from os2mo_http_trigger_protocol import RequestType  # noqa

# Common
VALID_FROM = "valid_from"
VALID_TO = "valid_to"
TO = "to"
FROM = "from"
NAME = "name"
GIVENNAME = "givenname"
SURNAME = "surname"
NICKNAME = "nickname"
NICKNAME_GIVENNAME = "nickname_givenname"
NICKNAME_SURNAME = "nickname_surname"
USER_KEY = "user_key"
VALUE = "value"
VALUE2 = "value2"
HREF = "href"
UUID = "uuid"
VALIDITY = "validity"
ORG = "org"
ORG_UNIT = "org_unit"
PERSON = "person"
JOB_FUNCTION = "job_function"
ITSYSTEM = "itsystem"
ADDRESS = "address"
ITSYSTEM_KEY = "IT-system"
EMPLOYEE = "employee"
LOCATION = "location"
USER_SETTINGS = "user_settings"
PRIMARY = "primary"
EXPLICITLY_PRIMARY = "explicitly-primary"
IS_PRIMARY = "is_primary"
SENIORITY = "seniority"
CHILDREN = "children"
DATA = "data"
TYPE = "type"
INFINITY = "infinity"
SCOPE = "scope"
NOTE = "note"

MINIMUM_PRIMARY_SCOPE_VALUE = 3000

# Address
ADDRESS_KEY = "Adresse"
ADDRESS_TYPE = "address_type"
VISIBILITY = "visibility"

# KLE
KLE_KEY = "KLE"
KLE_ASPECT = "kle_aspect"
KLE_NUMBER = "kle_number"

# Employee
CPR_NO = "cpr_no"
E = "e"

# Engagement
ENGAGEMENT_KEY = "Engagement"
ENGAGEMENT_TYPE = "engagement_type"
FRACTION = "fraction"
ENGAGEMENT = "engagement"

# Extensions
EXTENSION_1 = "udvidelse_1"

EXTENSION_ATTRIBUTE_MAPPING = [
    ("extension_1", EXTENSION_1),
    ("extension_2", "udvidelse_2"),
    ("extension_3", "udvidelse_3"),
    ("extension_4", "udvidelse_4"),
    ("extension_5", "udvidelse_5"),
    ("extension_6", "udvidelse_6"),
    ("extension_7", "udvidelse_7"),
    ("extension_8", "udvidelse_8"),
    ("extension_9", "udvidelse_9"),
    ("extension_10", "udvidelse_10"),
]

# Facet
FACETS = "facets"

# Association
ASSOCIATION = "association"
ASSOCIATION_KEY = "Tilknytning"
ASSOCIATION_TYPE = "association_type"
SUBSTITUTE = "substitute"
CLASSES = "dynamic_classes"
TRADE_UNION = "trade_union"

# Related units
RELATED_UNIT_KEY = "Relateret Enhed"

# Role type
ROLEBINDING_KEY = "Rollebinding"
ROLEBINDING_TYPE = "role"

# Leave
LEAVE_KEY = "Orlov"
LEAVE_TYPE = "leave_type"

# Manager
MANAGER_KEY = "Leder"
MANAGER = "manager"
MANAGER_TYPE = "manager_type"
MANAGER_LEVEL = "manager_level"
RESPONSIBILITY = "responsibility"

# Org unit
OU = "ou"
ORG_UNIT_TYPE = "org_unit_type"
TIME_PLANNING = "time_planning"
PARENT = "parent"
ORG_UNIT_LEVEL = "org_unit_level"
ORG_UNIT_HIERARCHY = "org_unit_hierarchy"

# Owner
OWNER = "owner"
OWNER_INFERENCE_PRIORITY = "owner_inference_priority"

# IT User
EXTERNAL_ID = "external_id"

# Auth
ADMIN = "admin"


class EntityType(enum.Enum):
    EMPLOYEE = E
    ORG_UNIT = OU


class OwnerInferencePriority(enum.Enum):
    engagement = "engagement_priority"
    association = "association_priority"


# LoRa names for org unit keys
ORG_UNIT_HIERARCHY_KEY = "opmærkning"

IT = "it"
KLE = "kle"
ROLEBINDING = "rolebinding"
LEAVE = "leave"
RELATED_UNIT = "related_unit"


class MoOrgFunk(enum.Enum):
    """
    Implemented MO-organisation functions. With non-trivial mapping to LoRa objs.
    """

    ENGAGEMENT = ENGAGEMENT
    ASSOCIATION = ASSOCIATION
    IT = IT
    KLE = KLE
    ROLEBINDING = ROLEBINDING
    ADDRESS = ADDRESS
    MANAGER = MANAGER
    OWNER = OWNER
    LEAVE = LEAVE
    RELATED_UNIT = RELATED_UNIT


RELATION_TRANSLATIONS = {
    ENGAGEMENT: ENGAGEMENT_KEY.lower(),
    ASSOCIATION: ASSOCIATION_KEY.lower(),
    IT: ITSYSTEM_KEY.lower(),
    KLE: KLE_KEY.lower(),
    ROLEBINDING: ROLEBINDING_KEY.lower(),
    ADDRESS: ADDRESS_KEY.lower(),
    MANAGER: MANAGER_KEY.lower(),
    OWNER: OWNER.lower(),
    LEAVE: LEAVE_KEY.lower(),
    RELATED_UNIT: RELATED_UNIT_KEY.lower(),
}

OBJECTTYPE = "objekttype"

#
# TYPES
#


@enum.unique
class FieldTypes(enum.IntEnum):
    """The different kinds of fields we support.

    NOTE: ADAPTED_ZERO_TO_MANY is used whenever a ZERO_TO_MANY field is used as
          as ZERO_TO_ONE field, and implements the necessary trickery to make
          it all appear correctly.
    """

    ZERO_TO_ONE, ZERO_TO_MANY, ADAPTED_ZERO_TO_MANY = range(3)


class FieldTuple:
    __slots__ = (
        "__path",
        "__type",
        "__filter_fn",
    )

    def __init__(
        self,
        path: tuple[str, str],
        type: FieldTypes,
        filter_fn: typing.Callable[[dict], bool] | None = None,
    ):
        self.__path = path
        self.__type = type
        self.__filter_fn = filter_fn

    def get(self, obj):
        try:
            props = functools.reduce(operator.getitem, self.path, obj)
        except (LookupError, TypeError):
            return []

        return list(filter(self.filter_fn, props))

    __call__ = get

    def _get_elems(self, obj, key):
        for item in self.get(obj):
            with suppress(KeyError):
                yield item[key]

    def get_uuids(self, obj):
        return self._get_elems(obj, "uuid")

    def get_uuid(self, obj):
        return next(self.get_uuids(obj), None)

    @property
    def path(self) -> tuple[str, str]:
        return self.__path

    @property
    def type(self) -> FieldTypes:
        return self.__type

    @property
    def filter_fn(self) -> typing.Callable[[dict], bool] | None:
        return self.__filter_fn

    def __repr__(self):  # pragma: no cover
        return "{}({!r}, FieldTypes.{}, {!r})".format(
            type(self).__name__,
            self.path,
            self.type.name,
            self.filter_fn,
        )


#
# MAPPINGS
#


ORG_FUNK_GYLDIGHED_FIELD = FieldTuple(
    path=("tilstande", "organisationfunktiongyldighed"),
    type=FieldTypes.ZERO_TO_ONE,
)

ORG_FUNK_EGENSKABER_FIELD = FieldTuple(
    path=("attributter", "organisationfunktionegenskaber"),
    type=FieldTypes.ZERO_TO_ONE,
)

ORG_FUNK_UDVIDELSER_FIELD = FieldTuple(
    path=("attributter", "organisationfunktionudvidelser"),
    type=FieldTypes.ZERO_TO_ONE,
)

JOB_FUNCTION_FIELD = FieldTuple(
    path=("relationer", "opgaver"),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
)

ORG_FUNK_TYPE_FIELD = FieldTuple(
    path=("relationer", "organisatoriskfunktionstype"),
    type=FieldTypes.ZERO_TO_ONE,
)

ORG_FUNK_CLASSES_FIELD = FieldTuple(
    path=("relationer", "tilknyttedeklasser"),
    type=FieldTypes.ZERO_TO_MANY,
)

ASSOCIATED_ORG_UNIT_FIELD = FieldTuple(
    path=("relationer", "tilknyttedeenheder"),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
)

ASSOCIATED_FUNCTION_FIELD = FieldTuple(
    path=("relationer", "tilknyttedefunktioner"),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
)

ENGAGEMENT_FIELD = FieldTuple(
    path=("relationer", "tilknyttedefunktioner"),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
    # Not all tilknyttedefunktioner has an objekttype; use .get() to avoid KeyErrors.
    filter_fn=lambda x: x.get("objekttype") == ENGAGEMENT,
)

IT_USER_FIELD = FieldTuple(
    path=("relationer", "tilknyttedefunktioner"),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
    # Not all tilknyttedefunktioner has an objekttype; use .get() to avoid KeyErrors.
    filter_fn=lambda x: x.get("objekttype") == IT,
)

ASSOCIATED_MANAGER_ADDRESSES_FIELD = FieldTuple(
    path=("relationer", "tilknyttedefunktioner"),
    type=FieldTypes.ZERO_TO_MANY,
    # TODO: filter_fn
)

ASSOCIATED_ORG_UNITS_FIELD = FieldTuple(
    path=("relationer", "tilknyttedeenheder"),
    type=FieldTypes.ZERO_TO_MANY,
)

ASSOCIATED_ORG_FIELD = FieldTuple(
    path=("relationer", "tilknyttedeorganisationer"),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
)

ORG_UNIT_GYLDIGHED_FIELD = FieldTuple(
    path=("tilstande", "organisationenhedgyldighed"),
    type=FieldTypes.ZERO_TO_ONE,
)

ORG_UNIT_EGENSKABER_FIELD = FieldTuple(
    path=("attributter", "organisationenhedegenskaber"),
    type=FieldTypes.ZERO_TO_ONE,
)

ORG_UNIT_TYPE_FIELD = FieldTuple(
    path=("relationer", "enhedstype"),
    type=FieldTypes.ZERO_TO_ONE,
)

ORG_UNIT_LEVEL_FIELD = FieldTuple(
    path=("relationer", "niveau"),
    type=FieldTypes.ZERO_TO_ONE,
)

ORG_UNIT_HIERARCHY_FIELD = FieldTuple(
    path=("relationer", "opmærkning"),
    type=FieldTypes.ZERO_TO_MANY,
)

PARENT_FIELD = FieldTuple(
    path=("relationer", "overordnet"),
    type=FieldTypes.ZERO_TO_ONE,
)

PARENT_CLASS_FIELD = FieldTuple(
    path=("relationer", "overordnetklasse"),
    type=FieldTypes.ZERO_TO_ONE,
)

BELONGS_TO_FIELD = FieldTuple(
    path=("relationer", "tilhoerer"),
    type=FieldTypes.ZERO_TO_ONE,
)

USER_FIELD = FieldTuple(
    path=("relationer", "tilknyttedebrugere"),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
)

ADDRESSES_FIELD = FieldTuple(
    path=("relationer", "adresser"),
    type=FieldTypes.ZERO_TO_MANY,
)

SINGLE_ADDRESS_FIELD = FieldTuple(
    path=("relationer", "adresser"),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
)

ADDRESS_TYPE_FIELD = FieldTuple(
    path=("relationer", "organisatoriskfunktionstype"),
    type=FieldTypes.ZERO_TO_ONE,
)

KLE_ASPECT_FIELD = FieldTuple(
    path=("relationer", "opgaver"), type=FieldTypes.ADAPTED_ZERO_TO_MANY
)

RESPONSIBILITY_FIELD = FieldTuple(
    path=("relationer", "opgaver"),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
    filter_fn=lambda x: x["objekttype"] == "lederansvar",
)

MANAGER_LEVEL_FIELD = FieldTuple(
    path=("relationer", "opgaver"),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
    filter_fn=lambda x: x["objekttype"] == "lederniveau",
)

VISIBILITY_FIELD = FieldTuple(
    path=("relationer", "opgaver"),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
    filter_fn=lambda x: x["objekttype"] == "synlighed",
)

SINGLE_ITSYSTEM_FIELD = FieldTuple(
    path=("relationer", "tilknyttedeitsystemer"),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
)

EMPLOYEE_PERSON_FIELD = FieldTuple(
    path=("relationer", "tilknyttedepersoner"),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
)

EMPLOYEE_EGENSKABER_FIELD = FieldTuple(
    path=("attributter", "brugeregenskaber"),
    type=FieldTypes.ZERO_TO_ONE,
)

EMPLOYEE_UDVIDELSER_FIELD = FieldTuple(
    path=("attributter", "brugerudvidelser"),
    type=FieldTypes.ZERO_TO_ONE,
)

EMPLOYEE_GYLDIGHED_FIELD = FieldTuple(
    path=("tilstande", "brugergyldighed"),
    type=FieldTypes.ZERO_TO_ONE,
)

ORG_UNIT_TIME_PLANNING_FIELD = FieldTuple(
    path=("relationer", "opgaver"),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
    filter_fn=lambda x: x["objekttype"] == "tidsregistrering",
)

PRIMARY_FIELD = FieldTuple(path=("relationer", "primær"), type=FieldTypes.ZERO_TO_ONE)

EMPLOYEE_FIELDS = {
    EMPLOYEE_PERSON_FIELD,
    EMPLOYEE_EGENSKABER_FIELD,
    EMPLOYEE_GYLDIGHED_FIELD,
    BELONGS_TO_FIELD,
}

ENGAGEMENT_FIELDS = {
    ORG_FUNK_EGENSKABER_FIELD,
    ORG_FUNK_UDVIDELSER_FIELD,
    ORG_FUNK_GYLDIGHED_FIELD,
    JOB_FUNCTION_FIELD,
    ORG_FUNK_TYPE_FIELD,
    ASSOCIATED_ORG_UNIT_FIELD,
    ASSOCIATED_ORG_FIELD,
    USER_FIELD,
    PRIMARY_FIELD,
}

ASSOCIATION_FIELDS = {
    ORG_FUNK_EGENSKABER_FIELD,
    ORG_FUNK_GYLDIGHED_FIELD,
    JOB_FUNCTION_FIELD,
    ORG_FUNK_TYPE_FIELD,
    ORG_FUNK_CLASSES_FIELD,
    ASSOCIATED_ORG_UNIT_FIELD,
    ASSOCIATED_ORG_FIELD,
    ASSOCIATED_FUNCTION_FIELD,
    USER_FIELD,
    SINGLE_ADDRESS_FIELD,
    PRIMARY_FIELD,
    SINGLE_ITSYSTEM_FIELD,
}

ROLE_FIELDS = {
    ORG_FUNK_EGENSKABER_FIELD,
    ORG_FUNK_GYLDIGHED_FIELD,
    ORG_FUNK_TYPE_FIELD,
    ASSOCIATED_ORG_UNIT_FIELD,
    ASSOCIATED_ORG_FIELD,
    ORG_FUNK_CLASSES_FIELD,
    USER_FIELD,
    ASSOCIATED_FUNCTION_FIELD,
}

LEAVE_FIELDS = {
    ORG_FUNK_EGENSKABER_FIELD,
    ORG_FUNK_GYLDIGHED_FIELD,
    ORG_FUNK_TYPE_FIELD,
    ASSOCIATED_FUNCTION_FIELD,
    ASSOCIATED_ORG_FIELD,
    USER_FIELD,
}

MANAGER_FIELDS = {
    ORG_FUNK_EGENSKABER_FIELD,
    ORG_FUNK_GYLDIGHED_FIELD,
    ORG_FUNK_TYPE_FIELD,
    ASSOCIATED_ORG_UNIT_FIELD,
    ASSOCIATED_ORG_FIELD,
    USER_FIELD,
    RESPONSIBILITY_FIELD,
    MANAGER_LEVEL_FIELD,
}

OWNER_FIELDS = {
    ORG_FUNK_EGENSKABER_FIELD,
    ORG_FUNK_GYLDIGHED_FIELD,
    ORG_FUNK_TYPE_FIELD,
    ASSOCIATED_ORG_UNIT_FIELD,
    ASSOCIATED_ORG_FIELD,
    USER_FIELD,
    # RESPONSIBILITY_FIELD,
    # MANAGER_LEVEL_FIELD,
}

ORG_UNIT_FIELDS = {
    ORG_UNIT_EGENSKABER_FIELD,
    ORG_UNIT_GYLDIGHED_FIELD,
    ADDRESSES_FIELD,
    BELONGS_TO_FIELD,
    ORG_UNIT_TYPE_FIELD,
    ORG_UNIT_TIME_PLANNING_FIELD,
    PARENT_FIELD,
    ORG_UNIT_LEVEL_FIELD,
    ORG_UNIT_HIERARCHY_FIELD,
}

ITSYSTEM_FIELDS = {
    ORG_FUNK_EGENSKABER_FIELD,
    ORG_FUNK_UDVIDELSER_FIELD,
    ORG_FUNK_GYLDIGHED_FIELD,
    ASSOCIATED_ORG_UNIT_FIELD,
    ASSOCIATED_FUNCTION_FIELD,
    ASSOCIATED_ORG_FIELD,
    USER_FIELD,
    SINGLE_ITSYSTEM_FIELD,
}

ADDRESS_FIELDS = {
    ORG_FUNK_EGENSKABER_FIELD,
    SINGLE_ADDRESS_FIELD,
    ORG_FUNK_GYLDIGHED_FIELD,
    ASSOCIATED_ORG_UNIT_FIELD,
    ASSOCIATED_ORG_FIELD,
    USER_FIELD,
    ADDRESS_TYPE_FIELD,
    # Hard-coded here for now
    VISIBILITY_FIELD,
}

KLE_FIELDS = {
    ORG_FUNK_EGENSKABER_FIELD,
    ORG_FUNK_TYPE_FIELD,
    KLE_ASPECT_FIELD,
    ORG_FUNK_GYLDIGHED_FIELD,
    ASSOCIATED_ORG_UNIT_FIELD,
    ASSOCIATED_ORG_FIELD,
}
