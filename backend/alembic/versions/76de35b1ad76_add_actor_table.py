# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Add actor table."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "76de35b1ad76"
down_revision: str | None = "68ccf4b69392"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    table = op.create_table(
        "actor",
        sa.Column(
            "actor",
            sa.Uuid,
            primary_key=True,
        ),
        sa.Column("name", sa.String(255), nullable=False),
    )

    # List of well-known integrations fetched from:
    # * https://rammearkitektur.docs.magenta.dk/os2mo/tech-docs/audit-log.html
    actor_list = [
        ("AD2Mo Sync", "ad21105c-baad-c0de-6164-326d6f73796e"),
        ("ADGUID Sync", "ad5711c0-baad-c0de-0000-616467756964"),
        ("Calculate Primary", "ca1c0000-baad-c0de-6361-6c637072696d"),
        ("Developer", "de7e104e-baad-c0de-6465-76656c6f7065"),
        ("DIPEX", "d1fec000-baad-c0de-0000-004449504558"),
        ("Engagement Updater", "119da1e4-baad-c0de-656e-672075706461"),
        ("FKK", "f1c1c000-baad-c0de-0000-000000464b4b"),
        ("Job Function Configurator", "70bf1ccf-baad-c0de-6a6f-6266756e6366"),
        ("LDAP import export", "11101da9-baad-c0de-004d-4f206c646170"),
        ("Manager engagement elevator", "e1e7a104-baad-c0de-656c-657661746f72"),
        ("Manager Sync", "5d05711c-baad-c0de-7364-206d616e6167"),
        ("Omada", "0111ada0-baad-c0de-0000-006f6d616461"),
        ("Orggatekeeper", "ca1e4ee9-baad-c0de-6761-74656b656570"),
        ("Orgviewer (ADM)", "04c71e7a-baad-c0de-6f72-677669657761"),
        ("Orgviewer (Legacy)", "03800000-baad-c0de-006f-726776696577"),
        ("Orgviewer (MED)", "04c71e70-baad-c0de-6f72-677669657761"),
        ("OS2Sync", "0525711c-baad-c0de-006f-733273796e63"),
        ("SDChangedAt", "5dc4a1ce-baad-c0de-7364-6368616e6765"),
        ("SDMox", "5d111070-baad-c0de-0000-0073646d6f78"),
        ("SDTool", "5d100100-baad-c0de-0000-7364746f6f6c"),
        ("SDTool+", "5d700141-baad-c0de-0000-7364746f6f6c"),
        ("SMTP", "51111900-baad-c0de-6d6f-20736d747000"),
        ("SQLExport", "052ec901-baad-c0de-7371-6c6578706f72"),
    ]
    actors = [{"actor": actor, "name": name} for name, actor in actor_list]
    op.bulk_insert(table, actors)


def downgrade() -> None:
    op.drop_table("actor")
