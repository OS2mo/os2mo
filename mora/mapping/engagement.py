from mora.service.common import PropTypes, PropTuple

gyldighed = PropTuple(
    ('tilstande', 'organisationfunktiongyldighed'),
    PropTypes.ZERO_TO_ONE,
    lambda x: True
)

egenskaber = PropTuple(
    ('attributter', 'organisationfunktionegenskaber'),
    PropTypes.ZERO_TO_ONE,
    lambda x: True
)

job_title = PropTuple(
    ('relationer', 'opgaver'),
    PropTypes.ADAPTED_ZERO_TO_MANY,
    lambda x: True
)

engagement_type = PropTuple(
    ('relationer', 'organisatoriskfunktionstype'),
    PropTypes.ZERO_TO_ONE,
    lambda x: True
)

org_unit = PropTuple(
    ('relationer', 'tilknyttedeenheder'),
    PropTypes.ADAPTED_ZERO_TO_MANY,
    lambda x: True
)

org = PropTuple(
    ('relationer', 'tilknyttedeorganisationer'),
    PropTypes.ADAPTED_ZERO_TO_MANY,
    lambda x: True
)

user = PropTuple(
    ('relationer', 'tilknyttedebrugere'),
    PropTypes.ADAPTED_ZERO_TO_MANY,
    lambda x: True
)

props = {
    egenskaber,
    gyldighed,
    job_title,
    engagement_type,
    org_unit,
    org,
    user
}
