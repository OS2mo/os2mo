# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The built-in policies, hardcoded as the shape the database will later hold.

These express today's access - the public fields, the per-role `RBAC_MAP`
grants and the owner mutators - as policies of selector, read rules and
mutators. Enforcement against them lives in `mora.graphapi.schema`.
"""

from mora.graphapi.owner_entities import OWNER_ENTITIES
from mora.graphapi.policy import Mutator
from mora.graphapi.policy import Policy
from mora.graphapi.policy import ReadRule
from mora.graphapi.policy import Selector
from mora.graphapi.policy import SelectorKind
from mora.graphapi.policy import TypeRule

# (collection, public fields, relation fields) per collection type. The public
# fields (scalars, uuids, validity) are readable by every user; the relation
# fields (returning objects) require the reader role.
COLLECTION_FIELDS: tuple[tuple[str, frozenset[str], frozenset[str]], ...] = (
    (
        "address",
        frozenset(
            {
                "address_type_uuid",
                "employee_uuid",
                "engagement_uuid",
                "href",
                "ituser_uuid",
                "name",
                "org_unit_uuid",
                "resolve",
                "type",
                "user_key",
                "uuid",
                "validity",
                "value",
                "value2",
                "visibility_uuid",
            }
        ),
        frozenset(
            {
                "address_type",
                "address_type_response",
                "employee",
                "engagement",
                "engagement_response",
                "ituser",
                "ituser_response",
                "org_unit",
                "org_unit_response",
                "person",
                "person_response",
                "visibility",
                "visibility_response",
            }
        ),
    ),
    (
        "association",
        frozenset(
            {
                "association_type_uuid",
                "dynamic_class_uuid",
                "employee_uuid",
                "it_user_uuid",
                "job_function_uuid",
                "org_unit_uuid",
                "primary_uuid",
                "substitute_uuid",
                "trade_union_uuid",
                "type",
                "user_key",
                "uuid",
                "validity",
            }
        ),
        frozenset(
            {
                "association_type",
                "association_type_response",
                "dynamic_class",
                "dynamic_class_response",
                "employee",
                "it_user",
                "it_user_response",
                "job_function",
                "job_function_response",
                "org_unit",
                "org_unit_response",
                "person",
                "person_response",
                "primary",
                "primary_response",
                "substitute",
                "substitute_response",
                "trade_union",
                "trade_union_response",
            }
        ),
    ),
    (
        "class",
        frozenset(
            {
                "description",
                "example",
                "facet_uuid",
                "full_name",
                "it_system_uuid",
                "name",
                "org_uuid",
                "owner",
                "parent_uuid",
                "published",
                "scope",
                "type",
                "user_key",
                "uuid",
                "validity",
            }
        ),
        frozenset(
            {
                "children",
                "children_response",
                "facet",
                "facet_response",
                "it_system",
                "it_system_response",
                "owner_response",
                "parent",
                "parent_response",
                "top_level_facet",
            }
        ),
    ),
    (
        "employee",
        frozenset(
            {
                "cpr_no",
                "cpr_number",
                "given_name",
                "givenname",
                "name",
                "nickname",
                "nickname_given_name",
                "nickname_givenname",
                "nickname_surname",
                "seniority",
                "surname",
                "type",
                "user_key",
                "uuid",
                "validity",
            }
        ),
        frozenset(
            {
                "addresses",
                "addresses_response",
                "associations",
                "associations_response",
                "engagements",
                "engagements_response",
                "itusers",
                "itusers_response",
                "leaves",
                "leaves_response",
                "manager_roles",
                "manager_roles_response",
            }
        ),
    ),
    (
        "engagement",
        frozenset(
            {
                "employee_uuid",
                "engagement_type_uuid",
                "extension_1",
                "extension_10",
                "extension_2",
                "extension_3",
                "extension_4",
                "extension_5",
                "extension_6",
                "extension_7",
                "extension_8",
                "extension_9",
                "fraction",
                "is_primary",
                "job_function_uuid",
                "leave_uuid",
                "org_unit_uuid",
                "primary_uuid",
                "type",
                "user_key",
                "uuid",
                "validity",
            }
        ),
        frozenset(
            {
                "addresses_response",
                "employee",
                "engagement_type",
                "engagement_type_response",
                "itusers",
                "itusers_response",
                "job_function",
                "job_function_response",
                "leave",
                "leave_response",
                "managers",
                "org_unit",
                "org_unit_response",
                "person",
                "person_response",
                "primary",
                "primary_response",
            }
        ),
    ),
    (
        "facet",
        frozenset(
            {
                "description",
                "org_uuid",
                "parent_uuid",
                "published",
                "type",
                "user_key",
                "uuid",
                "validity",
            }
        ),
        frozenset(
            {
                "children",
                "children_response",
                "classes",
                "classes_responses",
                "parent",
                "parent_response",
            }
        ),
    ),
    (
        "itsystem",
        frozenset({"name", "system_type", "type", "user_key", "uuid", "validity"}),
        frozenset({"roles", "roles_response"}),
    ),
    (
        "ituser",
        frozenset(
            {
                "binding_type",
                "employee_uuid",
                "engagement_uuid",
                "engagement_uuids",
                "external_id",
                "itsystem_uuid",
                "org_unit_uuid",
                "primary_uuid",
                "type",
                "user_key",
                "uuid",
                "validity",
            }
        ),
        frozenset(
            {
                "addresses",
                "addresses_response",
                "employee",
                "engagement",
                "engagement_response",
                "engagements",
                "engagements_responses",
                "itsystem",
                "itsystem_response",
                "org_unit",
                "org_unit_response",
                "person",
                "person_response",
                "primary",
                "primary_response",
                "rolebindings",
                "rolebindings_response",
            }
        ),
    ),
    (
        "kle",
        frozenset(
            {
                "kle_aspect_uuids",
                "kle_number_uuid",
                "org_unit_uuid",
                "type",
                "user_key",
                "uuid",
                "validity",
            }
        ),
        frozenset(
            {
                "kle_aspects",
                "kle_aspects_response",
                "kle_number",
                "kle_number_response",
                "org_unit",
                "org_unit_response",
            }
        ),
    ),
    (
        "leave",
        frozenset(
            {
                "employee_uuid",
                "engagement_uuid",
                "leave_type_uuid",
                "type",
                "user_key",
                "uuid",
                "validity",
            }
        ),
        frozenset(
            {
                "employee",
                "engagement",
                "engagement_response",
                "leave_type",
                "leave_type_response",
                "person",
                "person_response",
            }
        ),
    ),
    (
        "manager",
        frozenset(
            {
                "employee_uuid",
                "manager_level_uuid",
                "manager_type_uuid",
                "org_unit_uuid",
                "responsibility_uuids",
                "type",
                "user_key",
                "uuid",
                "validity",
            }
        ),
        frozenset(
            {
                "employee",
                "engagement_response",
                "manager_level",
                "manager_level_response",
                "manager_type",
                "manager_type_response",
                "org_unit",
                "org_unit_response",
                "person",
                "person_response",
                "responsibilities",
                "responsibilities_response",
            }
        ),
    ),
    (
        "org_unit",
        frozenset(
            {
                "name",
                "org_unit_hierarchy",
                "org_unit_level_uuid",
                "parent_uuid",
                "time_planning_uuid",
                "type",
                "unit_type_uuid",
                "user_key",
                "uuid",
                "validity",
            }
        ),
        frozenset(
            {
                "addresses",
                "addresses_response",
                "ancestors",
                "associations",
                "associations_response",
                "child_count",
                "children",
                "children_response",
                "engagements",
                "engagements_response",
                "has_children",
                "itusers",
                "itusers_response",
                "kles",
                "kles_response",
                "leaves",
                "leaves_response",
                "managers",
                "managers_response",
                "org_unit_hierarchy_model",
                "org_unit_level",
                "owners",
                "parent",
                "parent_response",
                "related_units",
                "related_units_response",
                "root",
                "root_response",
                "time_planning",
                "time_planning_response",
                "unit_hierarchy_response",
                "unit_level_response",
                "unit_type",
                "unit_type_response",
            }
        ),
    ),
    (
        "owner",
        frozenset(
            {
                "employee_uuid",
                "org_unit_uuid",
                "owner_inference_priority",
                "owner_uuid",
                "type",
                "user_key",
                "uuid",
                "validity",
            }
        ),
        frozenset(
            {
                "org_unit",
                "org_unit_response",
                "owner",
                "owner_response",
                "person",
                "person_response",
            }
        ),
    ),
    (
        "related_unit",
        frozenset({"org_unit_uuids", "type", "user_key", "uuid", "validity"}),
        frozenset({"org_units", "org_units_response"}),
    ),
    (
        "rolebinding",
        frozenset({"user_key", "uuid", "validity"}),
        frozenset(
            {
                "ituser",
                "ituser_response",
                "org_unit",
                "org_unit_response",
                "role",
                "role_response",
            }
        ),
    ),
)

# The GraphQL object type each collection's read rule applies to
COLLECTION_TYPE: dict[str, str] = {
    "address": "Address",
    "association": "Association",
    "class": "Class",
    "employee": "Employee",
    "engagement": "Engagement",
    "facet": "Facet",
    "itsystem": "ITSystem",
    "ituser": "ITUser",
    "kle": "KLE",
    "leave": "Leave",
    "manager": "Manager",
    "org_unit": "OrganisationUnit",
    "owner": "Owner",
    "related_unit": "RelatedUnit",
    "rolebinding": "RoleBinding",
}

# The response and registration wrapper fields, readable by everyone for every
# collection they wrap
RESPONSE_FIELDS = frozenset(
    {"current", "objects", "registrations", "uuid", "validities"}
)
REGISTRATION_FIELDS = frozenset(
    {
        "actor",
        "actor_object",
        "current",
        "end",
        "model",
        "note",
        "registration_id",
        "start",
        "uuid",
        "validities",
    }
)

# Scalar value types every user may read, whatever collection they hang off
SCALAR_TYPE_GRANTS = frozenset(
    {
        ("DARAddress", f)
        for f in {
            "description",
            "door",
            "floor",
            "house_number",
            "href",
            "latitude",
            "longitude",
            "municipality_code",
            "name",
            "road_code",
            "road_name",
            "streetmap_href",
            "supplementary_city",
            "value",
            "zip_code",
            "zip_code_name",
        }
    }
    | {("DefaultAddress", "value")}
    | {("MultifieldAddress", f) for f in {"name", "value", "value2"}}
    | {("OpenValidity", f) for f in {"from", "to"}}
    | {("Validity", f) for f in {"from", "to"}}
    | {("PageInfo", "next_cursor")}
    | {("UUIDPaged", f) for f in {"objects", "page_info"}}
)


# The wrapper types for a collection: its response, paged and registration
# types. Employee is reached through Person, so it has no bare registration type
def _wrapper_grants(type_name: str) -> frozenset[tuple[str, str]]:
    grants = frozenset(
        {(f"{type_name}Response", f) for f in RESPONSE_FIELDS}
        | {(f"{type_name}ResponsePaged", f) for f in {"objects", "page_info"}}
        | {(f"{type_name}ResponseRegistration", f) for f in REGISTRATION_FIELDS}
    )
    if type_name != "Employee":
        grants |= {(f"{type_name}Registration", f) for f in REGISTRATION_FIELDS}
    return grants


# The registration types for employee (Person) and the audit-log readouts
REGISTRATION_TYPE_GRANTS = frozenset(
    {("PersonRegistration", f) for f in REGISTRATION_FIELDS}
    | {
        ("Registration", f)
        for f in {
            "actor",
            "actor_object",
            "end",
            "model",
            "note",
            "registration_id",
            "start",
            "uuid",
        }
    }
    | {("RegistrationPaged", f) for f in {"objects", "page_info"}}
    | {("IRegistrationPaged", f) for f in {"objects", "page_info"}}
)


# Public structural types: health, version, the caller, the organisation and the
# actor and event readouts, each reachable without a role
PUBLIC_TYPE_GRANTS = frozenset(
    {("Health", f) for f in {"identifier", "status"}}
    | {("HealthPaged", f) for f in {"objects", "page_info"}}
    | {("Version", f) for f in {"lora_version", "mo_hash", "mo_version"}}
    | {("Myself", f) for f in {"actor", "email", "roles", "username"}}
    | {
        ("Organisation", f)
        for f in {"municipality_code", "name", "type", "user_key", "uuid"}
    }
    | {("SpecialActor", f) for f in {"display_name", "key", "uuid"}}
    | {("UnknownActor", f) for f in {"display_name", "error", "uuid"}}
    | {("ActorPaged", f) for f in {"objects", "page_info"}}
    | {
        ("AccessLog", f)
        for f in {"actor", "actor_object", "id", "model", "time", "uuids"}
    }
    | {("AccessLogPaged", f) for f in {"objects", "page_info"}}
    | {
        ("File", f)
        for f in {"base64_contents", "file_name", "file_store", "text_contents"}
    }
    | {("FilePaged", f) for f in {"objects", "page_info"}}
    | {("Event", f) for f in {"priority", "subject", "token"}}
    | {("FullEvent", f) for f in {"priority", "silenced", "subject"}}
    | {("FullEventPaged", f) for f in {"objects", "page_info"}}
    | {("Listener", f) for f in {"owner", "routing_key", "user_key", "uuid"}}
    | {("ListenerPaged", f) for f in {"objects", "page_info"}}
    | {("Namespace", f) for f in {"name", "owner", "public"}}
    | {("NamespacePaged", f) for f in {"objects", "page_info"}}
    # The public query fields
    | {("Query", f) for f in {"healths", "me", "version"}}
)

# The reader query fields: one entry point per collection
READER_QUERY_FIELDS = frozenset(
    {
        "access_log",
        "actors",
        "addresses",
        "associations",
        "classes",
        "employees",
        "engagements",
        "event_listeners",
        "event_namespaces",
        "events",
        "facets",
        "files",
        "itsystems",
        "itusers",
        "kles",
        "leaves",
        "managers",
        "org",
        "org_units",
        "owners",
        "persons",
        "registrations",
        "related_units",
        "rolebindings",
    }
)

# The reader's event and actor relation fields, hanging off the public types
READER_TYPE_GRANTS = frozenset(
    {("FullEvent", "listener")}
    | {("Listener", f) for f in {"events", "namespace"}}
    | {("Namespace", "listeners")}
    | {
        (actor, field)
        for actor in {"SpecialActor", "UnknownActor"}
        for field in {"event_listeners", "event_namespaces"}
    }
)

# The admin-only fields with no collection (event and file operations)
ADMIN_QUERY_FIELDS = frozenset({"event_fetch"})
ADMIN_MUTATOR_NAMES = frozenset(
    {
        "event_acknowledge",
        "event_rerun",
        "event_send",
        "event_silence",
        "event_unsilence",
        "upload_file",
    }
)


def _collection_read_rules(public: bool) -> tuple[ReadRule, ...]:
    """One read rule per collection: its public fields, or its relation fields."""
    return tuple(
        ReadRule(
            collection=collection, fields=public_fields if public else relation_fields
        )
        for collection, public_fields, relation_fields in COLLECTION_FIELDS
    )


def _wrapper_type_rule() -> TypeRule:
    """The response/paged/registration wrappers, readable by everyone."""
    grants = frozenset().union(
        *(_wrapper_grants(type_name) for type_name in COLLECTION_TYPE.values())
    )
    return TypeRule(grants=grants | SCALAR_TYPE_GRANTS | REGISTRATION_TYPE_GRANTS)


# Public: every user may read the public collection fields and the public types
PUBLIC = Policy(
    name="Public",
    selector=Selector(kind=SelectorKind.ALL),
    readers=_collection_read_rules(public=True),
    types=TypeRule(grants=_wrapper_type_rule().grants | PUBLIC_TYPE_GRANTS),
)

# Reader: additionally reads the relation fields and the collection entry points
READER = Policy(
    name="Reader",
    selector=Selector(kind=SelectorKind.ROLE, value="reader"),
    readers=_collection_read_rules(public=False),
    types=TypeRule(
        grants=frozenset({("Query", f) for f in READER_QUERY_FIELDS})
        | READER_TYPE_GRANTS
    ),
)

# Admin: runs every mutator, plus the collection-less admin fields
ADMIN = Policy(
    name="Admin",
    selector=Selector(kind=SelectorKind.ROLE, value="admin"),
    mutators=tuple(Mutator(name=name) for name in sorted(OWNER_ENTITIES))
    + tuple(Mutator(name=name) for name in sorted(ADMIN_MUTATOR_NAMES)),
    types=TypeRule(grants=frozenset({("Query", f) for f in ADMIN_QUERY_FIELDS})),
)

# Owner: runs the mutators it owns, checked against the database at enforcement
OWNER = Policy(
    name="Owner",
    selector=Selector(kind=SelectorKind.ROLE, value="owner"),
    mutators=tuple(Mutator(name=name) for name in sorted(OWNER_ENTITIES)),
)

# The built-in policies, in the order they grant
POLICIES: tuple[Policy, ...] = (PUBLIC, READER, ADMIN, OWNER)
