# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Normalise seeded actor names to Keycloak service-account usernames."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "68559a270001"
down_revision: str | Sequence[str] | None = "6163746f7273"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


actor = sa.table(
    "actor",
    sa.column("actor", sa.Uuid),
    sa.column("name", sa.Text),
)

actor_list = [
    ("ad21105c-baad-c0de-6164-326d6f73796e", "service-account-ad2mo_sync"),
    ("ad5711c0-baad-c0de-0000-616467756964", "service-account-adguid_sync"),
    ("a1705000-baad-c0de-0000-000061706f73", "service-account-apos"),
    ("ca1c0000-baad-c0de-6361-6c637072696d", "service-account-calculate_primary"),
    ("d1fec000-baad-c0de-0000-004449504558", "service-account-dipex"),
    ("de7e104e-baad-c0de-6465-76656c6f7065", "service-account-developer"),
    ("119da1e4-baad-c0de-656e-672075706461", "service-account-engagement_updater"),
    ("f1c1c000-baad-c0de-0000-000000464b4b", "service-account-fkk"),
    (
        "70bf1ccf-baad-c0de-6a6f-6266756e6366",
        "service-account-job_function_configurator",
    ),
    ("11101da9-baad-c0de-004d-4f206c646170", "service-account-ldap_import_export"),
    ("5d05711c-baad-c0de-7364-206d616e6167", "service-account-manager_sync"),
    (
        "e1e7a104-baad-c0de-656c-657661746f72",
        "service-account-manager_engagement_elevator",
    ),
    ("0525711c-baad-c0de-006f-733273796e63", "service-account-os2sync_export"),
    ("0111ada0-baad-c0de-0000-006f6d616461", "service-account-omada"),
    ("ca1e4ee9-baad-c0de-6761-74656b656570", "service-account-orggatekeeper"),
    ("04c71e7a-baad-c0de-6f72-677669657761", "service-account-orgviewer_adm"),
    ("03800000-baad-c0de-006f-726776696577", "service-account-orgviewer"),
    ("04c71e70-baad-c0de-6f72-677669657761", "service-account-orgviewer_med"),
    ("5dc4a1ce-baad-c0de-7364-6368616e6765", "service-account-sd_changed_at"),
    ("5d111070-baad-c0de-0000-0073646d6f78", "service-account-sdmox"),
    ("5d100100-baad-c0de-0000-7364746f6f6c", "service-account-sdtool"),
    ("5d700141-baad-c0de-0000-7364746f6f6c", "service-account-sdtool_plus"),
    ("51111900-baad-c0de-6d6f-20736d747000", "service-account-smtp"),
    ("052ec901-baad-c0de-7371-6c6578706f72", "service-account-sql_export"),
    ("3aca9ef1-baad-c0de-6d61-6e6167657274", "service-account-manager_terminator"),
    ("8f107777-baad-c0de-7866-6c6f77000000", "service-account-xflow"),
]


def upgrade() -> None:
    for actor_uuid, name in actor_list:
        op.execute(actor.update().where(actor.c.actor == actor_uuid).values(name=name))


def downgrade() -> None:
    pass
