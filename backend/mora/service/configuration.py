# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from fastapi import APIRouter

from mora import conf_db
from mora import config

router = APIRouter()


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
        show_it_associations_tab=settings.show_it_associations_tab,
    )
    return configuration
