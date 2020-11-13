"""Insert missing default configuration settings.

Revision ID: 97b811d05c40
Revises: 2818f2a406c9
Create Date: 2020-11-13 15:07:58.487450
"""
from operator import itemgetter

from alembic import op
from mora.conf_db.alembic.helpers.config_v1 import Config
from mora.conf_db.alembic.helpers.session import get_session
from sqlalchemy.sql import select

# revision identifiers, used by Alembic.
revision = "97b811d05c40"
down_revision = "2818f2a406c9"
branch_labels = None
depends_on = None

# This is the default key-value configuration pairs. They are used to
# initialize the configuration database through.
_DEFAULT_CONF = (
    ("show_roles", "True"),
    ("show_kle", "False"),
    ("show_user_key", "True"),
    ("show_location", "True"),
    ("show_time_planning", "False"),
    ("show_level", "True"),
    ("show_primary_engagement", "False"),
    ("show_primary_association", "False"),
    ("show_org_unit_button", "False"),
    ("inherit_manager", "True"),
    ("read_only", "False"),
    # Comma seperated UUID(s) of top-level facets to show on association view.
    ("association_dynamic_facets", ""),
)


def _find_missing_default_keys(session):
    """Check for missing default settings."""
    query = select([Config.setting]).where(
        Config.object == None  # noqa: E711
    )
    result = session.execute(query)
    settings_in_db = set(map(itemgetter(0), result))
    default = set(map(itemgetter(0), _DEFAULT_CONF))
    missing = default - settings_in_db
    return missing


def _insert_missing_defaults(session, missing):
    print("Inserting missing default configuration values {}.".format(missing))
    missing_values = dict(filter(lambda x: x[0] in missing, _DEFAULT_CONF))
    for setting, value in missing_values.items():
        entry = Config(object=None, setting=setting, value=value)
        session.add(entry)


def upgrade():
    """Insert missing default settings, if any"""
    bind = op.get_bind()
    with get_session(bind) as session:
        missing = _find_missing_default_keys(session)
        if missing:
            _insert_missing_defaults(session, missing)


def downgrade():
    """Noop downgrade.

    As we cannot know which particular keys were inserted on upgrade.
    """
    pass
