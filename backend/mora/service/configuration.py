# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from fastapi import APIRouter, Body
from uuid import UUID
import logging
from .. import util, conf_db, settings

logger = logging.getLogger("mo_configuration")

router = APIRouter()


@router.post('/ou/{unitid}/configuration')
def set_org_unit_configuration(unitid: UUID, configuration: dict = Body(...)):
    """Set a configuration setting for an ou.

    .. :quickref: Unit; Create configuration setting.

    :statuscode 201: Setting created.

    :param unitid: The UUID of the organisational unit to be configured.

    :<json object conf: Configuration option

    .. sourcecode:: json

      {
        "org_units": {
          "show_location": "True"
        }
      }

    :returns: True
    """
    unitid = str(unitid)
    return conf_db.set_configuration(configuration, unitid)


@router.get('/ou/{unitid}/configuration')
def get_org_unit_configuration(unitid: UUID):
    """Read configuration settings for an ou.

    .. :quickref: Unit; Read configuration setting.

    :statuscode 200: Setting returned.

    :param unitid: The UUID of the organisational unit.

    :returns: Configuration settings for unit
    """
    unitid = str(unitid)
    configuration = conf_db.get_configuration(unitid)
    return configuration


@router.post('/configuration')
def set_global_configuration(configuration: dict = Body(...)):
    """Set or modify a gloal configuration setting.

    .. :quickref: Set or modify a global configuration setting.

    :statuscode 201: Setting created.

    :<json object conf: Configuration option

    .. sourcecode:: json

      {
        "org_units": {
          "show_roles": "False"
        }
      }

    :returns: True
    """
    return conf_db.set_configuration(configuration)


@router.get('/configuration')
def get_global_configuration():
    """Read configuration settings for an ou.

    .. :quickref: Unit; Read configuration setting.

    :statuscode 200: Setting returned.
    :statuscode 404: No such unit found.

    :returns: Global configuration settings
    """

    configuration = conf_db.get_configuration()
    return configuration


@router.get('/navlinks')
def get_navlinks():
    """Retrieve nav links.

    .. :quickref: Unit; Retrieve nav links

    :statuscode 200: Nav link list returned.

    :returns: A list of nav links
    """

    navlinks = settings.config.get("navlinks", [{}])
    return navlinks
