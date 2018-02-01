#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#


'''
Engagements
-----------

This section describes how to interact with employee engagements.

'''

import collections
import itertools

import flask

from mora import lora
from mora.service.common import (create_organisationsfunktion_payload,
                                 ensure_bounds, inactivate_old_interval,
                                 inactivate_org_funktion,
                                 update_payload)
from mora.service.mapping import (ENGAGEMENT_FIELDS, ORG_FUNK_TYPE_FIELD,
                                  JOB_TITLE_FIELD, ORG_FUNK_GYLDIGHED_FIELD,
                                  ORG_UNIT_FIELD)
from . import common, employee, facet, org
from .. import util

blueprint = flask.Blueprint('engagements', __name__, static_url_path='',
                            url_prefix='/service')
ENGAGEMENT_KEY = 'Engagement'

JOB_TITLE = 'job_title'
ENGAGEMENT_TYPE = 'engagement_type'
ORG_UNIT = 'org_unit'
ORG = 'org'

FUNCTION_TYPES = {
    'engagement': 'Engagement',
    'association': 'Tilknytning',
}


@blueprint.route('/<any("e", "ou"):type>/<uuid:id>/details/')
def list_details(type, id):
    c = common.get_connector()

    r = []

    if type == 'e':
        search = dict(tilknyttedebrugere=id)
    else:
        assert type == 'ou', 'bad type ' + type
        search = dict(tilknyttedeenheder=id)

    search.update(virkningfra='-infinity', virkningtil='infinity')

    r = {
        functype: bool(
            c.organisationfunktion(funktionsnavn=funcname, **search),
        )
        for functype, funcname in FUNCTION_TYPES.items()
    }

    if type == 'e':
        def get_systems(reg):
            if not reg:
                return

            yield from reg['relationer'].get('tilknyttedeitsystemer', [])

        regs = c.bruger.get(
            id,
            virkningfra='-infinity',
            virkningtil='infinity',
        )

        r['it'] = any(rel.get('uuid') for rel in get_systems(regs))

    return flask.jsonify(r)


@blueprint.route(
    '/<any("e", "ou"):type>/<uuid:id>/details/<function>',
)
@util.restrictargs('at', 'validity', 'start', 'limit')
def get_engagement(type, id, function):
    '''Obtain the list of engagements corresponding to a user or
    organisational unit.

    .. :quickref: Engagement; List

    :queryparam date at: Current time in ISO-8601 format.
    :queryparam string validity: Only show *past*, *present* or
        *future* values -- which the default being to show *present*
        values.
    :queryparam int start: Index of first item for paging.
    :queryparam int limit: Maximum items.

    :param type: 'ou' for querying a unit; 'e' for querying an
        employee.
    :param uuid id: The UUID to query, i.e. the ID of the employee or
        unit.
    :param function: See :http:get:`/service/(any:type)/(uuid:id)/details/`
        for the available values for this field.

    :<jsonarr object job_function:
        See :http:get:`/service/o/(uuid:orgid)/f/(facet)/`.
    :<jsonarr object type:
        See :http:get:`/service/o/(uuid:orgid)/f/(facet)/`.
    :<jsonarr object org_unit:
        See :http:get:`/service/o/(uuid:orgid)/f/(facet)/`.
    :<jsonarr string uuid: Machine-friendly UUID.
    :<jsonarr string valid_from: The from date, in ISO 8601.
    :<jsonarr string valid_to: The to date, in ISO 8601.

    :status 200: Always.

    **Example response**:

    .. sourcecode:: json

      [
            {
                "job_function": {
                    "example": null,
                    "name": "Fakultet",
                    "scope": null,
                    "user_key": "fak",
                    "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6"
                },
                "org_unit": {
                    "name": "Humanistisk fakultet",
                    "user_key": "hum",
                    "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
                },
                "person": {
                    "cpr_no": "1111111111",
                    "name": "Anders And",
                    "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
                },
                "type": {
                    "example": null,
                    "name": "Afdeling",
                    "scope": null,
                    "user_key": "afd",
                    "uuid": "32547559-cfc1-4d97-94c6-70b192eff825"
                },
                "uuid": "d000591f-8705-4324-897a-075e3623f37b",
                "valid_from": "2017-01-01T00:00:00+01:00",
                "valid_to": null
            }
        ]

    '''

    c = common.get_connector()

    if type == 'e':
        search = dict(tilknyttedebrugere=id)
    else:
        assert type == 'ou', 'bad type ' + type
        search = dict(tilknyttedeenheder=id)

    # ensure that we report an error correctly
    if function not in FUNCTION_TYPES:
        raise ValueError('invalid function type {!r}'.format(function))

    search.update(
        limit=int(flask.request.args.get('limit', 0)) or 20,
        start=int(flask.request.args.get('start', 0)),
        funktionsnavn=FUNCTION_TYPES[function],
    )

    # all these caches are overkill when just listing one engagement,
    # but frequently helpful when listing all engagements for a unit
    functions = dict(c.organisationfunktion.get_all(**search))

    def get_employee_id(effect):
        return effect['relationer']['tilknyttedebrugere'][-1]['uuid']

    def get_unit_id(effect):
        return effect['relationer']['tilknyttedeenheder'][-1]['uuid']

    def get_type_id(effect):
        try:
            rels = effect['relationer']
            return rels['organisatoriskfunktionstype'][-1]['uuid']
        except (KeyError, IndexError):
            return None

    def get_title_id(effect):
        try:
            return effect['relationer']['opgaver'][-1]['uuid']
        except (KeyError, IndexError):
            return None

    class_cache = {
        classid: classid and facet.get_one_class(c, classid, classobj)
        for classid, classobj in c.klasse.get_all(
            uuid=itertools.chain(
                map(get_title_id, functions.values()),
                map(get_type_id, functions.values()),
            )
        )
    }

    user_cache = {
        userid: employee.get_one_employee(c, userid, user, with_cpr=True)
        for userid, user in
        c.bruger.get_all(uuid={
            get_employee_id(v) for v in functions.values()
        })
    }

    unit_cache = {
        unitid: org.get_one_orgunit(
            c, unitid, unit, details=org.UnitDetails.MINIMAL,
        )
        for unitid, unit in
        c.organisationenhed.get_all(
            uuid=map(get_unit_id,
                     functions.values()),
        )
    }

    class_cache[None] = user_cache[None] = unit_cache[None] = None

    return flask.jsonify([
        {
            "uuid": funcid,

            "person": user_cache[get_employee_id(effect)],
            "org_unit": unit_cache[get_unit_id(effect)],
            "job_function": class_cache[get_title_id(effect)],
            "type": class_cache[get_type_id(effect)],

            "valid_from": util.to_iso_time(start),
            "valid_to": util.to_iso_time(end),
        }

        for funcid, funcobj in functions.items()
        for start, end, effect in c.organisationfunktion.get_effects(
            funcobj,
            {
                'relationer': (
                    'opgaver',
                    'organisatoriskfunktionstype',
                    'tilknyttedeenheder',
                ),
                'tilstande': (
                    'organisationfunktiongyldighed',
                ),
            },
            {
                'attributter': (
                    'organisationfunktionegenskaber',
                ),
                'relationer': (
                    'tilhoerer',
                    'tilknyttedebrugere',
                    'tilknyttedeorganisationer',
                ),
            },
            virkningfra='-infinity',
            virkningtil='infinity',
        )
        if effect.get('tilstande')
                 .get('organisationfunktiongyldighed')[0]
                 .get('gyldighed') == 'Aktiv'
    ])


def create_engagement(employee_uuid, req):
    # TODO: Validation

    org_unit_uuid = req.get(ORG_UNIT).get('uuid')
    org_uuid = req.get(ORG).get('uuid')
    job_title_uuid = req.get(JOB_TITLE).get('uuid')
    engagement_type_uuid = req.get(ENGAGEMENT_TYPE).get('uuid')
    valid_from = req.get('valid_from')
    valid_to = req.get('valid_to', 'infinity')

    bvn = "{} {} {}".format(employee_uuid, org_unit_uuid, ENGAGEMENT_KEY)

    engagement = create_organisationsfunktion_payload(
        funktionsnavn=ENGAGEMENT_KEY,
        valid_from=valid_from,
        valid_to=valid_to,
        brugervendtnoegle=bvn,
        tilknyttedebrugere=[employee_uuid],
        tilknyttedeorganisationer=[org_uuid],
        tilknyttedeenheder=[org_unit_uuid],
        funktionstype=engagement_type_uuid,
        opgaver=[job_title_uuid]
    )

    lora.Connector().organisationfunktion.create(engagement)


def edit_engagement(employee_uuid, req):
    engagement_uuid = req.get('uuid')
    # Get the current org-funktion which the user wants to change
    c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
    original = c.organisationfunktion.get(uuid=engagement_uuid)

    data = req.get('data')
    new_from = data.get('valid_from')
    new_to = data.get('valid_to', 'infinity')

    payload = dict()
    payload['note'] = 'Rediger engagement'

    overwrite = req.get('overwrite')
    if overwrite:
        # We are performing an update
        old_from = overwrite.get('valid_from')
        old_to = overwrite.get('valid_to')
        payload = inactivate_old_interval(
            old_from, old_to, new_from, new_to, payload,
            ('tilstande', 'organisationfunktiongyldighed')
        )

    update_fields = list()

    # Always update gyldighed
    update_fields.append((
        ORG_FUNK_GYLDIGHED_FIELD,
        {'gyldighed': "Aktiv"}
    ))

    if JOB_TITLE in data.keys():
        update_fields.append((
            JOB_TITLE_FIELD,
            {'uuid': data.get(JOB_TITLE).get('uuid')}
        ))

    if ENGAGEMENT_TYPE in data.keys():
        update_fields.append((
            ORG_FUNK_TYPE_FIELD,
            {'uuid': data.get(ENGAGEMENT_TYPE).get('uuid')},
        ))

    if ORG_UNIT in data.keys():
        update_fields.append((
            ORG_UNIT_FIELD,
            {'uuid': data.get(ORG_UNIT).get('uuid')},
        ))

    payload = update_payload(new_from, new_to, update_fields, original,
                             payload)

    bounds_fields = list(
        ENGAGEMENT_FIELDS.difference({x[0] for x in update_fields}))
    payload = ensure_bounds(new_from, new_to, bounds_fields, original, payload)

    c.organisationfunktion.update(payload, engagement_uuid)


def terminate_engagement(engagement_uuid, enddate):
    """
    Terminate the given engagement at the given date

    :param engagement_uuid: An engagement UUID
    :param enddate: The date of termination
    """
    c = lora.Connector(effective_date=enddate)

    orgfunk = c.organisationfunktion.get(engagement_uuid)

    # Create inactivation object
    startdate = [
        g['virkning']['from'] for g in
        orgfunk['tilstande']['organisationfunktiongyldighed']
        if g['gyldighed'] == 'Aktiv'
    ][0]

    payload = inactivate_org_funktion(startdate, enddate, "Afslut engagement")
    c.organisationfunktion.update(payload, engagement_uuid)
