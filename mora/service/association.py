#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

'''
Associations
-----------

This section describes how to interact with employee associations.

'''

import flask

from mora import lora
from mora.service.common import create_organisationsfunktion_payload

blueprint = flask.Blueprint('associations', __name__, static_url_path='',
                            url_prefix='/service')

ASSOCIATION_KEY = 'Tilknytning'


def create_association(employee_uuid, req):
    # TODO: Validation

    org_unit_uuid = req.get('org_unit_uuid')
    org_uuid = req.get('org_uuid')
    job_title_uuid = req.get('job_title_uuid')
    association_type_uuid = req.get('association_type_uuid')
    valid_from = req.get('valid_from')
    valid_to = req.get('valid_to')

    bvn = "{} {} {}".format(employee_uuid, org_unit_uuid, ASSOCIATION_KEY)

    association = create_organisationsfunktion_payload(
        funktionsnavn=ASSOCIATION_KEY,
        valid_from=valid_from,
        valid_to=valid_to,
        brugervendtnoegle=bvn,
        tilknyttedebrugere=[employee_uuid],
        tilknyttedeorganisationer=[org_uuid],
        tilknyttedeenheder=[org_unit_uuid],
        funktionstype=association_type_uuid,
        opgaver=[job_title_uuid]
    )

    lora.Connector().organisationfunktion.create(association)


def edit_association(employee_uuid, req):
    # TODO
    pass


def terminate_association(association_uuid, enddate):
    # TODO
    pass
