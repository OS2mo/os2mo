# SPDX-FileCopyrightText: 2022 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

"""index fk columns '*_registrering_id'

Revision ID: b27228471604
Revises: initial
Create Date: 2022-04-05 11:05:57.832331
"""
import os

from alembic import op
from sqlalchemy.orm import sessionmaker


# revision identifiers, used by Alembic.
revision = "b27228471604"
down_revision = "initial"
branch_labels = None
depends_on = None


Session = sessionmaker()


def _apply_sql_from_file(relpath: str):
    path = os.path.join(os.path.dirname(__file__), relpath)
    bind = op.get_bind()
    session = Session(bind=bind)
    with open(path) as sql:
        session.execute(sql.read())


def upgrade():
    _apply_sql_from_file("b27228471604_index_fk_columns__registrering_id__upgrade.sql")


def downgrade():
    _apply_sql_from_file(
        "b27228471604_index_fk_columns__registrering_id__downgrade.sql"
    )
