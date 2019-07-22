#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import enum
import functools
import operator
import typing

# Common

VALID_FROM = 'valid_from'
VALID_TO = 'valid_to'
TO = 'to'
FROM = 'from'
NAME = 'name'
GIVENNAME = 'givenname'
SURNAME = 'surname'
USER_KEY = 'user_key'
VALUE = 'value'
HREF = 'href'
UUID = 'uuid'
URN = 'urn'
VALIDITY = 'validity'
ORG = 'org'
ORG_UNIT = 'org_unit'
PERSON = 'person'
JOB_FUNCTION = 'job_function'
ITSYSTEM = 'itsystem'
ADDRESS = 'address'
ITSYSTEM_KEY = 'IT-system'
EMPLOYEE = "employee"
LOCATION = 'location'
ERROR = 'error'
USER_SETTINGS = 'user_settings'
INTEGRATION_DATA = 'integration_data'
PRIMARY = 'primary'
ON_BEFORE = "before"
ON_AFTER = "after"

# Address
ADDRESS_KEY = 'Adresse'
ADDRESS_TYPE = 'address_type'
VISIBILITY = 'visibility'

# Employee
CPR_NO = 'cpr_no'


# Engagement
ENGAGEMENT_KEY = 'Engagement'
ENGAGEMENT_TYPE = 'engagement_type'
FRACTION = 'fraction'

# Association
ASSOCIATION_KEY = 'Tilknytning'
ASSOCIATION_TYPE = 'association_type'

# Related units
RELATED_UNIT_KEY = 'Relateret Enhed'

# Role type
ROLE_KEY = 'Rolle'
ROLE_TYPE = 'role_type'

# Leave
LEAVE_KEY = 'Orlov'
LEAVE_TYPE = 'leave_type'

# Manager
MANAGER_KEY = 'Leder'
MANAGER = 'manager'
MANAGER_TYPE = 'manager_type'
MANAGER_LEVEL = 'manager_level'
RESPONSIBILITY = 'responsibility'
MANAGER_ADDRESS_TYPE = 'manager_address_type'

# Org unit
ORG_UNIT_TYPE = 'org_unit_type'
TIME_PLANNING = 'time_planning'
PARENT = 'parent'
ADDRESSES = 'addresses'

RELATION_TRANSLATIONS = {
    'engagement': ENGAGEMENT_KEY.lower(),
    'association': ASSOCIATION_KEY.lower(),
    'it': ITSYSTEM_KEY.lower(),
    'role': ROLE_KEY.lower(),
    'address': ADDRESS_KEY.lower(),
    'manager': MANAGER_KEY.lower(),
    'leave': LEAVE_KEY.lower(),
}


#
# TYPES
#

@enum.unique
class FieldTypes(enum.IntEnum):
    '''The different kinds of fields we support'''
    ZERO_TO_ONE, ZERO_TO_MANY, ADAPTED_ZERO_TO_MANY = range(3)


class FieldTuple(object):
    __slots__ = (
        '__path',
        '__type',
        '__filter_fn',
    )

    def __init__(self, path: typing.Tuple[str, str], type: FieldTypes,
                 filter_fn: typing.Callable[[dict], bool]=None):
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

    def get_uuids(self, obj):
        for item in self.get(obj):
            try:
                yield item['uuid']
            except KeyError:
                pass

    def get_uuid(self, obj):
        return next(self.get_uuids(obj), None)

    @property
    def path(self) -> typing.Tuple[str, str]:
        return self.__path

    @property
    def type(self) -> FieldTypes:
        return self.__type

    @property
    def filter_fn(self) -> typing.Optional[typing.Callable[[dict], bool]]:
        return self.__filter_fn

    def __repr__(self):
        return '{}({!r}, FieldTypes.{}, {!r})'.format(
            type(self).__name__,
            self.path,
            self.type.name,
            self.filter_fn,
        )


#
# MAPPINGS
#


ORG_FUNK_GYLDIGHED_FIELD = FieldTuple(
    path=('tilstande', 'organisationfunktiongyldighed'),
    type=FieldTypes.ZERO_TO_ONE,
)

ORG_FUNK_EGENSKABER_FIELD = FieldTuple(
    path=('attributter', 'organisationfunktionegenskaber'),
    type=FieldTypes.ZERO_TO_ONE,
)

ORG_FUNK_UDVIDELSER_FIELD = FieldTuple(
    path=('attributter', 'organisationfunktionudvidelser'),
    type=FieldTypes.ZERO_TO_ONE,
)

ORG_FUNK_TYPE_FIELD = FieldTuple(
    path=('relationer', 'organisatoriskfunktionstype'),
    type=FieldTypes.ZERO_TO_ONE,
)

JOB_FUNCTION_FIELD = FieldTuple(
    path=('relationer', 'opgaver'),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
)

ORG_FUNK_TYPE_FIELD = FieldTuple(
    path=('relationer', 'organisatoriskfunktionstype'),
    type=FieldTypes.ZERO_TO_ONE,
)

ASSOCIATED_ORG_UNIT_FIELD = FieldTuple(
    path=('relationer', 'tilknyttedeenheder'),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
)

ASSOCIATED_FUNCTION_FIELD = FieldTuple(
    path=('relationer', 'tilknyttedefunktioner'),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
)

ASSOCIATED_MANAGER_ADDRESSES_FIELD = FieldTuple(
    path=('relationer', 'tilknyttedefunktioner'),
    type=FieldTypes.ZERO_TO_MANY
)

ASSOCIATED_ORG_UNITS_FIELD = FieldTuple(
    path=('relationer', 'tilknyttedeenheder'),
    type=FieldTypes.ZERO_TO_MANY,
)

ASSOCIATED_ORG_FIELD = FieldTuple(
    path=('relationer', 'tilknyttedeorganisationer'),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
)

ORG_UNIT_GYLDIGHED_FIELD = FieldTuple(
    path=('tilstande', 'organisationenhedgyldighed'),
    type=FieldTypes.ZERO_TO_ONE,
)

ORG_UNIT_EGENSKABER_FIELD = FieldTuple(
    path=('attributter', 'organisationenhedegenskaber'),
    type=FieldTypes.ZERO_TO_ONE,
)

ORG_UNIT_TYPE_FIELD = FieldTuple(
    path=('relationer', 'enhedstype'),
    type=FieldTypes.ZERO_TO_ONE,
)

PARENT_FIELD = FieldTuple(
    path=('relationer', 'overordnet'),
    type=FieldTypes.ZERO_TO_ONE,
)

BELONGS_TO_FIELD = FieldTuple(
    path=('relationer', 'tilhoerer'),
    type=FieldTypes.ZERO_TO_ONE,
)

USER_FIELD = FieldTuple(
    path=('relationer', 'tilknyttedebrugere'),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
)

ADDRESSES_FIELD = FieldTuple(
    path=('relationer', 'adresser'),
    type=FieldTypes.ZERO_TO_MANY,
)

SINGLE_ADDRESS_FIELD = FieldTuple(
    path=('relationer', 'adresser'),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
)

FUNCTION_ADDRESS_FIELD = FieldTuple(
    path=('relationer', 'tilknyttedefunktioner'),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
)

ADDRESS_TYPE_FIELD = FieldTuple(
    path=('relationer', 'organisatoriskfunktionstype'),
    type=FieldTypes.ZERO_TO_ONE,
)

MANAGER_TYPE_FIELD = FieldTuple(
    path=('relationer', 'organisatoriskfunktionstype'),
    type=FieldTypes.ZERO_TO_ONE,
)

RESPONSIBILITY_FIELD = FieldTuple(
    path=('relationer', 'opgaver'),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
    filter_fn=lambda x: x['objekttype'] == 'lederansvar'
)

MANAGER_LEVEL_FIELD = FieldTuple(
    path=('relationer', 'opgaver'),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
    filter_fn=lambda x: x['objekttype'] == 'lederniveau'
)

VISIBILITY_FIELD = FieldTuple(
    path=('relationer', 'opgaver'),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
    filter_fn=lambda x: x['objekttype'] == 'synlighed'
)

SINGLE_ITSYSTEM_FIELD = FieldTuple(
    path=('relationer', 'tilknyttedeitsystemer'),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
)

EMPLOYEE_PERSON_FIELD = FieldTuple(
    path=('relationer', 'tilknyttedepersoner'),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
)

EMPLOYEE_EGENSKABER_FIELD = FieldTuple(
    path=('attributter', 'brugeregenskaber'),
    type=FieldTypes.ZERO_TO_ONE,
)

EMPLOYEE_UDVIDELSER_FIELD = FieldTuple(
    path=('attributter', 'brugerudvidelser'),
    type=FieldTypes.ZERO_TO_ONE,
)

EMPLOYEE_GYLDIGHED_FIELD = FieldTuple(
    path=('tilstande', 'brugergyldighed'),
    type=FieldTypes.ZERO_TO_ONE,
)

ORG_UNIT_TIME_PLANNING_FIELD = FieldTuple(
    path=('relationer', 'opgaver'),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
    filter_fn=lambda x: x['objekttype'] == 'tidsregistrering'
)

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
    USER_FIELD
}

ASSOCIATION_FIELDS = {
    ORG_FUNK_EGENSKABER_FIELD,
    ORG_FUNK_GYLDIGHED_FIELD,
    JOB_FUNCTION_FIELD,
    ORG_FUNK_TYPE_FIELD,
    ASSOCIATED_ORG_UNIT_FIELD,
    ASSOCIATED_ORG_FIELD,
    USER_FIELD,
    SINGLE_ADDRESS_FIELD,
}

ROLE_FIELDS = {
    ORG_FUNK_EGENSKABER_FIELD,
    ORG_FUNK_GYLDIGHED_FIELD,
    ORG_FUNK_TYPE_FIELD,
    ASSOCIATED_ORG_UNIT_FIELD,
    ASSOCIATED_ORG_FIELD,
    USER_FIELD,
}

LEAVE_FIELDS = {
    ORG_FUNK_EGENSKABER_FIELD,
    ORG_FUNK_GYLDIGHED_FIELD,
    ORG_FUNK_TYPE_FIELD,
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
    ASSOCIATED_MANAGER_ADDRESSES_FIELD,
}

ORG_UNIT_FIELDS = {
    ORG_UNIT_EGENSKABER_FIELD,
    ORG_UNIT_GYLDIGHED_FIELD,
    ADDRESSES_FIELD,
    BELONGS_TO_FIELD,
    ORG_UNIT_TYPE_FIELD,
    ORG_UNIT_TIME_PLANNING_FIELD,
    PARENT_FIELD
}

ITSYSTEM_FIELDS = {
    ORG_FUNK_EGENSKABER_FIELD,
    ORG_FUNK_GYLDIGHED_FIELD,
    ASSOCIATED_ORG_UNIT_FIELD,
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
    VISIBILITY_FIELD
}
