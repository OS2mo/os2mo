# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Change first parameter name of _json_object_delete_keys.

Changed from "json" to "jsonblob". Without this, MO could not run on PostgreSQL
17.0 and newer.
"""

from collections.abc import Sequence

from alembic import op
from sqlalchemy import text

revision: str = "b1533c198dab"
down_revision: str | Sequence[str] | None = "2fa1af1af332"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        text("""
DROP FUNCTION _json_object_delete_keys(json,text[]);

CREATE FUNCTION actual_state._json_object_delete_keys(jsonblob json, keys_to_delete text[]) RETURNS json
    LANGUAGE sql IMMUTABLE STRICT
    AS $$
SELECT COALESCE(
  (SELECT ('{' || string_agg(to_json(key) || ':' || value::json::text, ',') || '}')
   FROM json_each(jsonblob)
   WHERE key not in (select key from unnest(keys_to_delete) as a(key))),
  '{}'
)::json
$$;
    """)
    )
