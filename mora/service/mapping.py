#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from mora.service.common import FieldTuple, FieldTypes

ORG_FUNK_GYLDIGHED_FIELD = FieldTuple(
    ('tilstande', 'organisationfunktiongyldighed'),
    FieldTypes.ZERO_TO_ONE,
    lambda x: True
)

ORG_FUNK_EGENSKABER_FIELD = FieldTuple(
    ('attributter', 'organisationfunktionegenskaber'),
    FieldTypes.ZERO_TO_ONE,
    lambda x: True
)

JOB_TITLE_FIELD = FieldTuple(
    ('relationer', 'opgaver'),
    FieldTypes.ADAPTED_ZERO_TO_MANY,
    lambda x: True
)

ENGAGEMENT_TYPE_FIELD = FieldTuple(
    ('relationer', 'organisatoriskfunktionstype'),
    FieldTypes.ZERO_TO_ONE,
    lambda x: True
)

ORG_UNIT_FIELD = FieldTuple(
    ('relationer', 'tilknyttedeenheder'),
    FieldTypes.ADAPTED_ZERO_TO_MANY,
    lambda x: True
)

ORG_FIELD = FieldTuple(
    ('relationer', 'tilknyttedeorganisationer'),
    FieldTypes.ADAPTED_ZERO_TO_MANY,
    lambda x: True
)

USER_FIELD = FieldTuple(
    ('relationer', 'tilknyttedebrugere'),
    FieldTypes.ADAPTED_ZERO_TO_MANY,
    lambda x: True
)

ENGAGEMENT_FIELDS = {
    ORG_FUNK_EGENSKABER_FIELD,
    ORG_FUNK_GYLDIGHED_FIELD,
    JOB_TITLE_FIELD,
    ENGAGEMENT_TYPE_FIELD,
    ORG_UNIT_FIELD,
    ORG_FIELD,
    USER_FIELD
}
