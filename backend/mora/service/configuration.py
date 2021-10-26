# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from structlog import get_logger
from uuid import UUID

from fastapi import APIRouter, Body

from .. import conf_db, config

logger = get_logger()

router = APIRouter()


@router.post("/ou/{unitid}/configuration", status_code=410)
def set_org_unit_configuration(unitid: UUID, configuration: dict = Body(...)) -> bool:
    """Removed configuration setting endpoint.

    :statuscode 410: Endpoint removed.

    :param unitid: Unused UUID.

    :<json object conf: Unused json body

    .. sourcecode:: json

      {
        "org_units": {
          "show_location": "True"
        }
      }

    :returns: False
    """
    return False


@router.get("/ou/{unitid}/configuration")
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


@router.post("/configuration", status_code=410)
def set_global_configuration(configuration: dict = Body(...)) -> bool:
    """Removed global configuration setting endpoint.

    :statuscode 410: Endpoint removed.

    :<json object conf: Unused json body

    .. sourcecode:: json

      {
        "org_units": {
          "show_roles": "False"
        }
      }

    :returns: False
    """
    return False


@router.get("/configuration")
def get_global_configuration():
    """Read configuration settings for an ou.

    .. :quickref: Unit; Read configuration setting.

    :statuscode 200: Setting returned.
    :statuscode 404: No such unit found.

    :returns: Global configuration settings
    """

    settings = config.get_settings()

    # TODO: Remove once #44717 is merged (ConfDB removal).
    # Then, return `settings` instead.
    configuration = conf_db.get_configuration()
    configuration.update(
        confdb_autocomplete_use_new_api=settings.confdb_autocomplete_use_new_api,
    )
    return configuration


@router.get("/navlinks")
def get_navlinks():
    """Retrieve nav links.

    .. :quickref: Unit; Retrieve nav links

    :statuscode 200: Nav link list returned.

    :returns: A list of nav links
    """

    navlinks = config.get_settings().navlinks
    if not navlinks:
        navlinks = [{}]
    return navlinks
