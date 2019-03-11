#
# Copyright (c) Magenta ApS
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

from .. import exceptions
from .. import mapping
from .. import util
from ..integrations.serviceplatformen import get_citizen


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

    try:
        sp_data = get_citizen(cpr)
    except KeyError:
        exceptions.ErrorCodes.V_NO_PERSON_FOR_CPR(cpr=cpr)
    except ValueError:
        exceptions.ErrorCodes.V_CPR_NOT_VALID(cpr=cpr)
    except Exception:
        exceptions.ErrorCodes.E_UNKNOWN(cpr=cpr)
    return flask.jsonify(format_cpr_response(sp_data, cpr))


def format_cpr_response(sp_data: dict, cpr: str):
    first_name = sp_data.get('fornavn')
    middle_name = sp_data.get('mellemnavn')
    last_name = sp_data.get('efternavn')

    # Filter empty name components, and construct full name string
    name = ' '.join(filter(None, [first_name, middle_name, last_name]))

    return {
        mapping.NAME: name,
        mapping.CPR_NO: cpr
    }
