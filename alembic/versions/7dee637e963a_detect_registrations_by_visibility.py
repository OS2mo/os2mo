# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""
Add the state and helper the event generation subsystem needs to detect new
registrations by transaction visibility instead of by wall-clock time.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "7dee637e963a"
down_revision: str | Sequence[str] | None = "9c00f43cd5a2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "alter table amqp_subsystem add column last_registration_snapshot pg_snapshot;"
    )
    op.execute("""
        update amqp_subsystem set last_registration_snapshot = pg_current_snapshot()
         where last_registration_snapshot is null;
    """)
    op.execute("""
        alter table amqp_subsystem
        alter column last_registration_snapshot set not null;
    """)
    op.execute("""
        create function committed_between(
            row_xmin xid,
            before pg_snapshot,
            after pg_snapshot
        ) returns boolean
        language sql
        immutable
        as $$
            -- DO NOT RE-USE THIS FUNCTION. IT ONLY WORKS FOR "RECENT" SNAPSHOTS.
            --
            -- Every row has an `xmin` column with the transaction id that inserted it.
            --
            -- Transaction ids (xid) are a 32-bit counter. To stay unique forever
            -- (after wrap-around), postgres pairs the 32-bit id/counter with an
            -- "epoch" (wrap count) to form the 64-bit xid8. It is just a complicated
            -- 64-bit number because the on-disk tuple header stores the 32-bit xid.
            --
            -- pg_visible_in_snapshot needs the `xid8`, but postgres has no xid->xid8
            -- cast, which is why it is done manually below.
            --
            -- ... and xid/xid8 don't even have arithmetic operators, so that is why we
            -- need the ::text::numeric conversion.
            --
            -- https://www.postgresql.org/docs/current/transaction-id.html
            -- https://www.postgresql.org/docs/current/functions-info.html#FUNCTIONS-INFO-SNAPSHOT
            --
            with reconstructed(xid8) as (
                -- greatest xid8 that is <= after's xmax and whose low 32 bits equal row_xmin.
                -- This only works for un-frozen rows (within one epoch of xmax),
                -- but is good enough here as we only care for recent registrations.
                select (xmax - ((xmax - row_xmin::text::numeric) % 4294967296))::text::xid8  -- evil floating point bit level hacking
                from (select pg_snapshot_xmax(after)::text::numeric as xmax) _  -- what the fuck?
            )
            -- a row is *newly* committed iff its xmin was not visible in `before` but
            -- is visible in `after`:
            select not pg_visible_in_snapshot(xid8, before)
                   and pg_visible_in_snapshot(xid8, after)
            from reconstructed
        $$;
    """)


def downgrade() -> None:
    op.execute("drop function committed_between(xid, pg_snapshot, pg_snapshot);")
    op.execute("alter table amqp_subsystem drop column last_registration_snapshot;")
