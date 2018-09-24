#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import collections
import enum

from . import util

# Common

VALID_FROM = 'valid_from'
VALID_TO = 'valid_to'
TO = 'to'
FROM = 'from'
NAME = 'name'
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

# Address
ADDRESS_KEY = 'Adresse'
ADDRESS_TYPE = 'address_type'

# Employee
CPR_NO = 'cpr_no'

# Engagement
ENGAGEMENT_KEY = 'Engagement'
ENGAGEMENT_TYPE = 'engagement_type'

# Association
ASSOCIATION_KEY = 'Tilknytning'
ASSOCIATION_TYPE = 'association_type'
LOCATION = 'location'

# Role type
ROLE_KEY = 'Rolle'
ROLE_TYPE = 'role_type'

# Leave
LEAVE_KEY = 'Orlov'
LEAVE_TYPE = 'leave_type'

# Manager
MANAGER_KEY = 'Leder'
MANAGER_TYPE = 'manager_type'
MANAGER_LEVEL = 'manager_level'
RESPONSIBILITY = 'responsibility'
MANAGER_ADDRESS_TYPE = 'manager_address_type'

# Org unit
ORG_UNIT_TYPE = 'org_unit_type'
NAME = 'name'
PARENT = 'parent'
ADDRESSES = 'addresses'
LOCATION = 'location'

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
    ZERO_TO_ONE = 0,
    ZERO_TO_MANY = 1,
    ADAPTED_ZERO_TO_MANY = 2,


class FieldTuple(collections.namedtuple(
    'FieldTuple',
    [
        'path',
        'type',
        'filter_fn'
    ]
)):
    def get(self, obj):
        return util.get_obj_value(obj, self.path, self.filter_fn)


#
# MAPPINGS
#

FUNCTION_KEYS = {
    'engagement': ENGAGEMENT_KEY,
    'association': ASSOCIATION_KEY,
    'role': ROLE_KEY,
    'leave': LEAVE_KEY,
    'manager': MANAGER_KEY,
    'it': ITSYSTEM_KEY,
}

ORG_FUNK_GYLDIGHED_FIELD = FieldTuple(
    path=('tilstande', 'organisationfunktiongyldighed'),
    type=FieldTypes.ZERO_TO_ONE,
    filter_fn=lambda x: True
)

ORG_FUNK_EGENSKABER_FIELD = FieldTuple(
    path=('attributter', 'organisationfunktionegenskaber'),
    type=FieldTypes.ZERO_TO_ONE,
    filter_fn=lambda x: True
)

ORG_FUNK_TYPE_FIELD = FieldTuple(
    path=('relationer', 'organisatoriskfunktionstype'),
    type=FieldTypes.ZERO_TO_ONE,
    filter_fn=lambda x: True
)

JOB_FUNCTION_FIELD = FieldTuple(
    path=('relationer', 'opgaver'),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
    filter_fn=lambda x: True
)

ORG_FUNK_TYPE_FIELD = FieldTuple(
    path=('relationer', 'organisatoriskfunktionstype'),
    type=FieldTypes.ZERO_TO_ONE,
    filter_fn=lambda x: True
)

ASSOCIATED_ORG_UNIT_FIELD = FieldTuple(
    path=('relationer', 'tilknyttedeenheder'),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
    filter_fn=lambda x: True
)

ASSOCIATED_ORG_FIELD = FieldTuple(
    path=('relationer', 'tilknyttedeorganisationer'),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
    filter_fn=lambda x: True
)

ORG_UNIT_GYLDIGHED_FIELD = FieldTuple(
    path=('tilstande', 'organisationenhedgyldighed'),
    type=FieldTypes.ZERO_TO_ONE,
    filter_fn=lambda x: True
)

ORG_UNIT_EGENSKABER_FIELD = FieldTuple(
    path=('attributter', 'organisationenhedegenskaber'),
    type=FieldTypes.ZERO_TO_ONE,
    filter_fn=lambda x: True
)

ORG_UNIT_TYPE_FIELD = FieldTuple(
    path=('relationer', 'enhedstype'),
    type=FieldTypes.ZERO_TO_ONE,
    filter_fn=lambda x: True
)

PARENT_FIELD = FieldTuple(
    path=('relationer', 'overordnet'),
    type=FieldTypes.ZERO_TO_ONE,
    filter_fn=lambda x: True
)

BELONGS_TO_FIELD = FieldTuple(
    path=('relationer', 'tilhoerer'),
    type=FieldTypes.ZERO_TO_ONE,
    filter_fn=lambda x: True
)

USER_FIELD = FieldTuple(
    path=('relationer', 'tilknyttedebrugere'),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
    filter_fn=lambda x: True
)

ADDRESSES_FIELD = FieldTuple(
    path=('relationer', 'adresser'),
    type=FieldTypes.ZERO_TO_MANY,
    filter_fn=lambda x: True
)

SINGLE_ADDRESS_FIELD = FieldTuple(
    path=('relationer', 'adresser'),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
    filter_fn=lambda x: True
)

MANAGER_TYPE_FIELD = FieldTuple(
    path=('relationer', 'organisatoriskfunktionstype'),
    type=FieldTypes.ZERO_TO_ONE,
    filter_fn=lambda x: True
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

SINGLE_ITSYSTEM_FIELD = FieldTuple(
    path=('relationer', 'tilknyttedeitsystemer'),
    type=FieldTypes.ADAPTED_ZERO_TO_MANY,
    filter_fn=lambda x: True
)

ENGAGEMENT_FIELDS = {
    ORG_FUNK_EGENSKABER_FIELD,
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
    SINGLE_ADDRESS_FIELD,
}

ORG_UNIT_FIELDS = {
    ORG_UNIT_EGENSKABER_FIELD,
    ORG_UNIT_GYLDIGHED_FIELD,
    ADDRESSES_FIELD,
    BELONGS_TO_FIELD,
    ORG_UNIT_TYPE_FIELD,
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
