# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

# Fields which are public: every user may access them.
PUBLIC_FIELDS: frozenset[tuple[str, str]] = frozenset(
    {
        ("Health", "identifier"),
        ("Health", "status"),
        ("HealthPaged", "objects"),
        ("HealthPaged", "page_info"),
        ("Myself", "actor"),
        ("Myself", "email"),
        ("Myself", "roles"),
        ("Myself", "username"),
        ("PageInfo", "next_cursor"),
        ("Query", "healths"),
        ("Query", "me"),
        ("Query", "version"),
        ("SpecialActor", "display_name"),
        ("SpecialActor", "key"),
        ("SpecialActor", "uuid"),
        ("UnknownActor", "display_name"),
        ("UnknownActor", "error"),
        ("UnknownActor", "uuid"),
        ("Version", "lora_version"),
        ("Version", "mo_hash"),
        ("Version", "mo_version"),
    }
)
