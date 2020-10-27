# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from operator import itemgetter
from sqlalchemy.sql import select
from sqlalchemy.orm import Session

from mora.conf_db.alembic.helpers.config_v1 import Config


def add_default_fields(session: Session, defaults):
    missing = _find_missing_default_keys(session, defaults)
    if missing:
        _insert_missing_defaults(session, missing, defaults)


def remove_default_fields(session: Session, defaults):
    default_keys = set(map(itemgetter(0), defaults))
    for key in default_keys:
        session.query(Config).filter(setting=key).delete()
        session.commit()


def _find_missing_default_keys(session, defaults):
    """Check for missing default settings."""
    query = select([Config.setting]).where(Config.object == None)  # noqa: E711
    result = session.execute(query)
    settings_in_db = set(map(itemgetter(0), result))
    default = set(map(itemgetter(0), defaults))
    missing = default - settings_in_db
    return missing


def _insert_missing_defaults(session, missing, defaults):
    print("Inserting missing default configuration values {}.".format(missing))
    missing_values = dict(filter(lambda x: x[0] in missing, defaults))
    for setting, value in missing_values.items():
        entry = Config(object=None, setting=setting, value=value)
        session.add(entry)
