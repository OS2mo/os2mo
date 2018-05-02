#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
"""
CPR
---

This section describes functionality for retrieving information about people
based on their CPR number.
"""

import flask

from mora import exceptions
from mora import util
from mora.integrations.serviceplatformen import get_citizen
from mora.service import keys

blueprint = flask.Blueprint('cpr', __name__, static_url_path='',
                            url_prefix='/service')


@blueprint.route('/e/cpr_lookup/')
@util.restrictargs(required=['q'])
def search_cpr():
    """
    Search for a CPR number in Serviceplatformen and retrieve the associated
    information

    :queryparam q: The CPR no. of a person to be searched

    :<jsonarr string name: The name of the person
    :<jsonarr string cpr_no: The person's CPR number.

    **Example Response**:

    .. sourcecode:: json

      {
        "name": "John Doe",
        "cpr_no": "0101501234"
      }

    """
    cpr = flask.request.args['q']

    if len(cpr) != 10:
        raise exceptions.ValidationError(
            'CPR no. should be 10 characters long',
        )

    sp_data = get_citizen(cpr)

    return flask.jsonify(format_cpr_response(sp_data, cpr))


def format_cpr_response(sp_data: dict, cpr: str):
    first_name = sp_data.get('fornavn')
    middle_name = sp_data.get('mellemnavn')
    last_name = sp_data.get('efternavn')

    # Filter empty name components, and construct full name string
    name = ' '.join(filter(None, [first_name, middle_name, last_name]))

    return {
        keys.NAME: name,
        keys.CPR_NO: cpr
    }
