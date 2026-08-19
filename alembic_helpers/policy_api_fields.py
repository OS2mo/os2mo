# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

# The policy API's own fields, which are public. Not part of the legacy
# PUBLIC_FIELDS snapshot.
POLICY_API_FIELDS: frozenset[tuple[str, str]] = frozenset(
    {
        ("Policy", "active"),
        ("Policy", "actors"),
        ("Policy", "description"),
        ("Policy", "name"),
        ("Policy", "rules"),
        ("Policy", "uuid"),
        ("PolicyActor", "kind"),
        ("PolicyActor", "uuid"),
        ("PolicyActor", "value"),
        ("PolicyPaged", "objects"),
        ("PolicyPaged", "page_info"),
        ("PolicyRule", "field"),
        ("PolicyRule", "type"),
        ("PolicyRule", "uuid"),
    }
)
