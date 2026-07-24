# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

# Fields which are introspection: every user may access them. `__typename` is a
# meta-field that can appear under any type; the __-prefixed introspection types
# carry the remaining introspection fields
INTROSPECTION_RULES: frozenset[tuple[str, str]] = frozenset(
    {
        ("*", "__typename"),
        ("Query", "__schema"),
        ("Query", "__type"),
        ("__Directive", "*"),
        ("__DirectiveLocation", "*"),
        ("__EnumValue", "*"),
        ("__Field", "*"),
        ("__InputValue", "*"),
        ("__Schema", "*"),
        ("__Type", "*"),
        ("__TypeKind", "*"),
    }
)
