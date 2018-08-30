#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
from mora.service.common import FieldTuple, FieldTypes

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

ITSYSTEMS_FIELD = FieldTuple(
    path=('relationer', 'tilknyttedeitsystemer'),
    type=FieldTypes.ZERO_TO_MANY,
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

ITSYSTEMS_FIELD = FieldTuple(
    path=('relationer', 'tilknyttedeitsystemer'),
    type=FieldTypes.ZERO_TO_MANY,
    filter_fn=lambda x: True
)
