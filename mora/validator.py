#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from mora import lora
from mora import util


def is_date_range_valid(parent: str, startdate: str, enddate: str) -> bool:
    """
    Determine if the given dates are within validity of the parent unit
    :param parent: The UUID of the parent unit
    :param startdate:
    :param enddate:
    :return:
    """

    assert util.parsedatetime(startdate) < util.parsedatetime(enddate)

    parent = lora.organisationenhed.get(
        uuid=parent,
        virkningfra=util.to_lora_time(startdate),
        virkningtil=util.to_lora_time(enddate),
    )

    validity = parent['tilstande']['organisationenhedgyldighed']

    if len(validity) == 1 and validity[0]['gyldighed'] == 'Aktiv':
        return True

    return False
