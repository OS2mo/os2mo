# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import enum
from collections.abc import Callable
from collections.abc import Collection
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING
from typing import Any
from uuid import UUID

import strawberry
from fastapi.encoders import jsonable_encoder
from sqlalchemy import ColumnElement
from sqlalchemy import and_
from sqlalchemy import exists
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy import true

from mora import db
from mora.auth.keycloak.models import Token
from mora.db import AsyncSession
from mora.graphapi.context import MOInfo
from mora.graphapi.filters import gen_filter_string
from mora.graphapi.policy_cel import build_activation
from mora.graphapi.policy_cel import build_filter_base_vars
from mora.graphapi.policy_cel import evaluate_condition
from mora.graphapi.policy_cel import evaluate_filter
from mora.graphapi.policy_cel import validate_filter

from .paged import CursorType
from .paged import LimitType
from .paged import ObjectsAndCursor
from .paged import paginate

if TYPE_CHECKING:  # pragma: no cover
    from mora.graphapi.filters import EmployeeFilter
    from mora.graphapi.filters import OrganisationUnitFilter
    from mora.graphapi.filters import OwnerFilter

# Type of strawberry's ``UNSET`` sentinel, mapped to ``null`` when exposing a
# mutator input to a filter expression (see `_input_map`).
_UNSET_TYPE = type(strawberry.UNSET)


@strawberry.enum(description="The kind of actor attribute a policy matches on.")
class PolicyActorKind(enum.Enum):
    # Matches an actor carrying this Keycloak token role/claim.
    role = "role"
    # Matches every actor regardless of attributes; the value is ignored.
    all = "all"


@strawberry.input(
    description=(
        "Actor filter. Limits policies to those applicable to an actor with the "
        "given roles. A policy matches if it has at least one actor matching any "
        "of the provided roles (or an `all` actor)."
    )
)
class PolicyActorFilter:
    roles: list[str] | None = strawberry.field(
        default=None, description=gen_filter_string("Actor role", "roles")
    )


@strawberry.input(description="Policy filter.")
class PolicyFilter:
    uuids: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("UUID", "uuids")
    )
    activated: bool | None = strawberry.field(
        default=None,
        description=(
            "Limit to policies with this activation state. When omitted or null, "
            "policies are not filtered by activation (set `true` for the "
            "currently-effective policies)."
        ),
    )
    actor: PolicyActorFilter | None = strawberry.field(
        default=None,
        description=(
            "Limit to policies applicable to an actor with these attributes. "
            "When omitted or null, policies are not filtered by actor."
        ),
    )


def _policy_actor_predicate(filter: PolicyActorFilter) -> ColumnElement:
    # Match by role. An absent (None) `roles` contributes nothing; an empty list
    # matches nothing. No roles provided (`{}`) means "has any actor" (existence
    # only).
    criteria: list[ColumnElement] = []
    if filter.roles is not None:
        criteria.append(
            and_(
                db.PolicyActor.kind == PolicyActorKind.role.value,
                db.PolicyActor.value.in_(filter.roles),
            )
        )
    if criteria:
        # An "all" actor matches every actor, so a policy with one satisfies any
        # role-based actor filter.
        criteria.append(db.PolicyActor.kind == PolicyActorKind.all.value)
        inner = or_(*criteria)
    else:
        # No roles provided (`{}`) means "has any actor" (existence only), which
        # already includes "all" actors.
        inner = true()
    return exists().where(db.PolicyActor.policy_fk == db.Policy.id).where(inner)


def policy_predicate(filter: PolicyFilter) -> ColumnElement:
    predicates: list[ColumnElement] = [true()]

    if filter.uuids is not None:
        predicates.append(db.Policy.id.in_(filter.uuids))

    if filter.activated is not None:
        predicates.append(db.Policy.activated == filter.activated)

    if filter.actor is not None:
        predicates.append(_policy_actor_predicate(filter.actor))

    return and_(*predicates)


def actor_filter_for(roles: Collection[str]) -> PolicyActorFilter:
    """Build the actor filter selecting policies applicable to an actor.

    The roles are passed as a concrete list (empty when the actor has none) so a
    roleless actor still matches `all` actors but nothing else -- as opposed to
    a null `roles`, which is the "match any actor" existence filter.
    """
    return PolicyActorFilter(roles=list(roles))


@strawberry.type(description="An actor a policy applies to.")
class PolicyActor:
    uuid: UUID = strawberry.field(description="UUID of the actor binding.")
    kind: PolicyActorKind = strawberry.field(
        description="The kind of attribute matched on."
    )
    value: str = strawberry.field(description="The value the attribute must equal.")


@strawberry.type(
    description=(
        "A resource a policy grants access to, expressed GraphQL-natively as a "
        "(type, field) pair."
    )
)
class PolicyRule:
    uuid: UUID = strawberry.field(description="UUID of the rule.")
    type: str = strawberry.field(
        description=(
            "GraphQL type the rule grants access to: a collection's object "
            'type, or "Query"/"Mutation".'
        )
    )
    field: str = strawberry.field(
        description='Field (or mutator) on the type, or "*" for all fields.'
    )
    condition: str | None = strawberry.field(
        description=(
            "Optional CEL condition that must evaluate true for the rule to "
            "grant access. Null means the rule is unconditional."
        )
    )
    filter: str | None = strawberry.field(
        description=(
            "Optional CEL expression returning one or more access-check specs "
            "`{collection, filter, check, field}`, each run as a SQL existence "
            "check; the rule only grants when all of them pass. Null means no "
            "entity restriction."
        )
    )


@strawberry.type(
    description=(
        "An access policy. A policy applies to a collection of actors and "
        "grants them access to a number of resources."
    )
)
class Policy:
    uuid: UUID = strawberry.field(description="UUID of the policy.")
    name: str = strawberry.field(description="Name of the policy.")
    description: str | None = strawberry.field(description="Description of the policy.")
    activated: bool = strawberry.field(description="Whether the policy is in effect.")

    @strawberry.field(description="Actors this policy applies to.")
    async def actors(root: "Policy", info: MOInfo) -> list[PolicyActor]:
        session: AsyncSession = info.context.session
        result = await session.scalars(
            select(db.PolicyActor)
            .where(db.PolicyActor.policy_fk == root.uuid)
            .order_by(db.PolicyActor.pk)
        )
        return [
            PolicyActor(
                uuid=actor.pk, kind=PolicyActorKind(actor.kind), value=actor.value
            )
            for actor in result
        ]

    @strawberry.field(description="Resources this policy grants access to.")
    async def rules(root: "Policy", info: MOInfo) -> list[PolicyRule]:
        session: AsyncSession = info.context.session
        result = await session.scalars(
            select(db.PolicyRule)
            .where(db.PolicyRule.policy_fk == root.uuid)
            .order_by(db.PolicyRule.pk)
        )
        return [
            PolicyRule(
                uuid=rule.pk,
                type=rule.type,
                field=rule.field,
                condition=rule.condition,
                filter=rule.filter,
            )
            for rule in result
        ]


def _to_policy(policy: "db.Policy") -> Policy:
    return Policy(
        uuid=policy.id,
        name=policy.name,
        description=policy.description,
        activated=policy.activated,
    )


async def policy_resolver(
    info: MOInfo,
    filter: PolicyFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> ObjectsAndCursor:
    if filter is None:
        filter = PolicyFilter()

    predicate = policy_predicate(filter=filter)
    query = select(db.Policy.id).where(predicate).order_by(db.Policy.id)
    session: AsyncSession = info.context.session
    uuids, next_cursor = await paginate(session, query, db.Policy.id, limit, cursor)

    result = await session.scalars(
        select(db.Policy).where(db.Policy.id.in_(uuids)).order_by(db.Policy.id)
    )
    return ObjectsAndCursor(
        objects=[_to_policy(policy) for policy in result],
        next_cursor=next_cursor,
    )


def validate_rule_filter(filter_value: str | None) -> None:
    """Reject a rule ``filter`` that is not a compilable CEL expression.

    Any rule may carry a filter. The filter is a CEL expression returning one
    or more check-specs; its result shape depends on runtime variables
    (``token``/``input``/``actor``/``current``), so declare time only
    compile-checks it. A compilable expression that yields a non-check-spec fails
    hard at permission-check time (see :func:`_entity_filter_grants`).
    """
    if filter_value is None:
        return
    validate_filter(filter_value)


def _reject_unknown_keys(data: dict, allowed: set[str], name: str) -> None:
    """Fail hard on filter keys outside ``allowed`` -- never silently drop one.

    The deserializers deliberately support only the subset of each filter type's
    fields the policies use; an author who writes a key that is misspelled or
    simply unsupported should get a loud error rather than a silently-ignored key
    (which could over- or under-grant).
    """
    unknown = set(data) - allowed
    if unknown:
        raise ValueError(f"unsupported {name} filter keys: {sorted(unknown)}")


_PERSON_FILTER_KEYS = {
    "uuids",
    "user_keys",
    "from_date",
    "to_date",
    "registration_time",
    "registration",
    "query",
    "cpr_numbers",
    "owner",
}


def _person_filter_from_dict(data: dict) -> "EmployeeFilter":
    """Build an ``EmployeeFilter`` from a plain mapping (the GraphQL shape)."""
    # Imported lazily: this module is imported by the schema layer, while the
    # filters module pulls in the wider GraphQL layer.
    from strawberry import UNSET

    from mora.graphapi.filters import EmployeeFilter
    from mora.graphapi.filters import EmployeeRegistrationFilter
    from mora.util import CPR

    if not isinstance(data, dict):
        raise ValueError("person filter must be an object")
    _reject_unknown_keys(data, _PERSON_FILTER_KEYS, "person")

    def dt(key: str) -> datetime | None:
        raw = data.get(key)
        return datetime.fromisoformat(raw) if raw is not None else None

    # `from_date`, `to_date` and `query` default to UNSET (not None) on
    # `EmployeeFilter`; preserve that distinction so an absent key behaves like
    # a normal query rather than forcing an explicit null.
    def absent_or_dt(key: str) -> datetime | None:
        return dt(key) if key in data else UNSET

    try:
        registration = None
        reg = data.get("registration")
        if reg is not None:
            registration = EmployeeRegistrationFilter(
                actors=(
                    [UUID(a) for a in reg["actors"]]
                    if reg.get("actors") is not None
                    else None
                ),
                start=(
                    datetime.fromisoformat(reg["start"])
                    if reg.get("start") is not None
                    else None
                ),
                end=(
                    datetime.fromisoformat(reg["end"])
                    if reg.get("end") is not None
                    else None
                ),
            )

        return EmployeeFilter(
            uuids=(
                [UUID(u) for u in data["uuids"]]
                if data.get("uuids") is not None
                else None
            ),
            user_keys=data.get("user_keys"),
            from_date=absent_or_dt("from_date"),
            to_date=absent_or_dt("to_date"),
            registration_time=dt("registration_time"),
            registration=registration,
            query=data.get("query", UNSET),
            cpr_numbers=(
                [CPR(c) for c in data["cpr_numbers"]]
                if data.get("cpr_numbers") is not None
                else None
            ),
            owner=(
                _owner_filter_from_dict(data["owner"])
                if data.get("owner") is not None
                else None
            ),
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(f"malformed person filter: {exc}") from exc


def _org_unit_filter_from_dict(data: dict) -> "OrganisationUnitFilter":
    """Build an ``OrganisationUnitFilter`` from a plain mapping.

    Supports only the subset the owner policies use: ``uuids``, the ``ancestor``
    sub-filter (for hierarchical ownership) and the ``owner`` sub-filter. Raises
    ``ValueError`` on an unsupported key or a malformed mapping.
    """
    from strawberry import UNSET

    from mora.graphapi.filters import OrganisationUnitFilter

    if not isinstance(data, dict):
        raise ValueError("org_unit filter must be an object")
    _reject_unknown_keys(data, {"uuids", "ancestor", "owner"}, "org_unit")

    try:
        return OrganisationUnitFilter(
            uuids=(
                [UUID(u) for u in data["uuids"]]
                if data.get("uuids") is not None
                else None
            ),
            # `ancestor` defaults to UNSET (no ancestor constraint); a literal
            # `None` means "root units", so preserve the absent-vs-null distinction.
            ancestor=(
                _org_unit_filter_from_dict(data["ancestor"])
                if data.get("ancestor") is not None
                else UNSET
            ),
            owner=(
                _owner_filter_from_dict(data["owner"])
                if data.get("owner") is not None
                else None
            ),
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(f"malformed org_unit filter: {exc}") from exc


def _owner_filter_from_dict(data: dict) -> "OwnerFilter":
    """Build an ``OwnerFilter`` from a plain mapping.

    ``OwnerFilter`` selects "owner" org-functions; its ``owner`` sub-filter (an
    ``EmployeeFilter``) is the *owning person*, while ``employee``/``org_unit``
    are the owned employee / org-unit. Supports exactly those keys plus ``uuids``
    (the org-function's own id). Raises ``ValueError`` on anything else.
    """
    from mora.graphapi.filters import OwnerFilter

    if not isinstance(data, dict):
        raise ValueError("owner filter must be an object")
    _reject_unknown_keys(data, {"uuids", "employee", "org_unit", "owner"}, "owner")

    try:
        return OwnerFilter(
            uuids=(
                [UUID(u) for u in data["uuids"]]
                if data.get("uuids") is not None
                else None
            ),
            employee=(
                _person_filter_from_dict(data["employee"])
                if data.get("employee") is not None
                else None
            ),
            org_unit=(
                _org_unit_filter_from_dict(data["org_unit"])
                if data.get("org_unit") is not None
                else None
            ),
            owner=(
                _person_filter_from_dict(data["owner"])
                if data.get("owner") is not None
                else None
            ),
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(f"malformed owner filter: {exc}") from exc


def _object_owner_filter_from_dict(filter_cls: type, data: dict) -> Any:
    """Build an object-collection filter from its owner sub-filter keys.

    The owner policies only ever constrain an object collection (ituser, address,
    engagement, ...) by its linked ``employee`` and/or ``org_unit``, so this
    knows exactly those two keys (a key the collection's filter type does not
    support surfaces as a ``TypeError`` -> ``ValueError``). An empty mapping
    yields an unconstrained filter (matches every object of the collection).
    """
    if not isinstance(data, dict):  # pragma: no cover - filter is dict-checked upstream
        raise ValueError(f"{filter_cls.__name__} filter must be an object")
    _reject_unknown_keys(data, {"employee", "org_unit"}, filter_cls.__name__)

    try:
        kwargs: dict[str, Any] = {}
        if data.get("employee") is not None:
            kwargs["employee"] = _person_filter_from_dict(data["employee"])
        if data.get("org_unit") is not None:
            kwargs["org_unit"] = _org_unit_filter_from_dict(data["org_unit"])
        return filter_cls(**kwargs)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"malformed {filter_cls.__name__} filter: {exc}") from exc


@dataclass(frozen=True)
class EntityFilterSpec:
    """How to evaluate a check-spec against one collection.

    ``from_dict`` turns a check-spec's filter map into the collection's MO filter,
    ``predicate`` builds the SQL predicate selecting matching objects (the
    collection's resolver predicate) and ``id_column`` is the column holding the
    object's uuid, against which a check-spec's ``field`` is matched.
    """

    from_dict: Callable[[dict], Any]
    predicate: Callable[[MOInfo, Any], ColumnElement]
    id_column: Any


# Cache for the lazily-built registry (see `_entity_filter_registry`).
_ENTITY_FILTER_REGISTRY: dict[str, EntityFilterSpec] | None = None


def _entity_filter_registry() -> dict[str, EntityFilterSpec]:
    """The lazily-built ``EntityFilterSpec`` registry keyed by collection.

    Built (and cached) on first use so the dependency on the resolver predicates
    and ORM tables (the wider GraphQL layer, which imports this module) stays out
    of import time. Covers every owner-protected collection: ``employee`` and
    ``org_unit`` (matched by their own uuid) and the org-function collections
    (matched by the org-function id).
    """
    global _ENTITY_FILTER_REGISTRY
    if _ENTITY_FILTER_REGISTRY is not None:
        return _ENTITY_FILTER_REGISTRY

    from mora.db import BrugerRegistrering
    from mora.db import OrganisationEnhedRegistrering
    from mora.db import OrganisationFunktionRegistrering
    from mora.graphapi import resolvers
    from mora.graphapi.filters import AddressFilter
    from mora.graphapi.filters import AssociationFilter
    from mora.graphapi.filters import EngagementFilter
    from mora.graphapi.filters import ITUserFilter
    from mora.graphapi.filters import KLEFilter
    from mora.graphapi.filters import LeaveFilter
    from mora.graphapi.filters import ManagerFilter
    from mora.graphapi.filters import RelatedUnitFilter
    from mora.graphapi.filters import RoleBindingFilter

    org_function_id = OrganisationFunktionRegistrering.organisationfunktion_id

    def obj(filter_cls: type, predicate: Callable) -> EntityFilterSpec:
        """An org-function collection spec (matched by the org-function id)."""

        def from_dict(data: dict) -> Any:
            return _object_owner_filter_from_dict(filter_cls, data)

        return EntityFilterSpec(
            from_dict=from_dict,
            predicate=predicate,
            id_column=org_function_id,
        )

    _ENTITY_FILTER_REGISTRY = {
        "employee": EntityFilterSpec(
            from_dict=_person_filter_from_dict,
            predicate=resolvers.employee_predicate,
            id_column=BrugerRegistrering.bruger_id,
        ),
        "org_unit": EntityFilterSpec(
            from_dict=_org_unit_filter_from_dict,
            predicate=resolvers.organisation_unit_predicate,
            id_column=OrganisationEnhedRegistrering.organisationenhed_id,
        ),
        "owner": EntityFilterSpec(
            from_dict=_owner_filter_from_dict,
            predicate=resolvers.owner_predicate,
            id_column=org_function_id,
        ),
        "address": obj(AddressFilter, resolvers.address_predicate),
        "association": obj(AssociationFilter, resolvers.association_predicate),
        "engagement": obj(EngagementFilter, resolvers.engagement_predicate),
        "ituser": obj(ITUserFilter, resolvers.it_user_predicate),
        "kle": obj(KLEFilter, resolvers.kle_predicate),
        "leave": obj(LeaveFilter, resolvers.leave_predicate),
        "manager": obj(ManagerFilter, resolvers.manager_predicate),
        "related_unit": obj(RelatedUnitFilter, resolvers.related_unit_predicate),
        "rolebinding": obj(RoleBindingFilter, resolvers.rolebinding_predicate),
    }
    return _ENTITY_FILTER_REGISTRY


def _entity_filter_spec(collection: str) -> EntityFilterSpec:
    """The :class:`EntityFilterSpec` for ``collection``.

    Raises :class:`EntityFilterError` for an unknown collection -- a check-spec
    naming one is a misconfigured rule and must fail hard, not silently deny.
    """
    try:
        return _entity_filter_registry()[collection]
    except KeyError as exc:
        raise EntityFilterError(
            f"check-spec on unsupported collection {collection!r}"
        ) from exc


def _input_map(arguments: dict) -> dict | list:
    """The mutator's argument exposed to a filter expression as ``input``.

    :func:`jsonable_encoder` coerces types (UUID/datetime/enum -> JSON-ish) and
    the ``custom_encoder`` maps strawberry ``UNSET`` to ``null`` (so unset fields
    read as ``null`` rather than a junk value), letting a filter read
    ``input.uuid``, ``input.person`` (``!= null`` to test presence), etc.
    Bare-argument mutators (delete) expose their scalar arguments directly, so
    ``input.uuid`` still works uniformly.

    Bulk mutators take a *list* input; it is passed through as a list, so a rule
    can require ownership of every item, e.g.
    ``input.map(i, {...check-spec keyed on i...})``.
    """
    raw = arguments.get("input")
    source = raw if raw is not None else arguments
    encoded = jsonable_encoder(source, custom_encoder={_UNSET_TYPE: lambda _: None})
    return encoded if isinstance(encoded, dict | list) else {}


class EntityFilterError(Exception):
    """A policy rule's entity filter could not be evaluated.

    Raised when a filtered rule cannot be evaluated against the request: an
    unknown collection, a malformed check-spec, missing field arguments or a
    filter expression that does not yield valid check-specs. These indicate a
    misconfigured rule or an unexpected mutator shape, which must fail hard
    (surface loudly) rather than silently deny -- a silent deny would mask the
    bug and could quietly drop access that the operator believes is granted.
    """


async def _resolve_actor(info: MOInfo, token: Token) -> str:
    """The calling actor's employee uuid, as a string (the lazy ``actor`` var).

    Uses the same resolution as the legacy owner check: by default the token's
    own uuid, or -- when configured -- the employee resolved via the authoritative
    IT-system. Faithful in both configurations.
    """
    from mora.auth.keycloak.rbac import _get_employee_uuid

    uuid = await _get_employee_uuid(token)
    # A caller without a resolvable employee uuid can own nothing. Fall back to
    # the nil UUID so ownership checks match no entity and deny cleanly, rather
    # than feeding a malformed value (e.g. ``str(None)``) into the entity filter
    # and raising a hard "badly formed UUID" error.
    return str(uuid) if uuid is not None else "00000000-0000-0000-0000-000000000000"


async def _load_current(info: MOInfo, arguments: dict) -> dict:
    """The existing object, as a CEL-friendly map (the lazy ``current`` var).

    Only the org-unit ``parent`` is exposed (the sole thing any rule needs, for
    the org-unit move case), mapped from the stored LoRa object so
    ``current.parent`` is a uuid string comparable to ``input.parent``. This is
    intentionally minimal and cheap to extend later.
    """
    from mora.auth.keycloak.uuid_extractor import _get_org_unit
    from mora.mapping import PARENT_FIELD

    input_map = _input_map(arguments)
    uuid = input_map.get("uuid") if isinstance(input_map, dict) else None
    # Only org_unit_update references `current`, and it always carries input.uuid.
    if uuid is None:  # pragma: no cover
        raise EntityFilterError("`current` requires input.uuid but none was provided")
    obj = await _get_org_unit(UUID(uuid))
    parent = PARENT_FIELD.get_uuid(obj) if obj is not None else None
    return {"parent": parent}


def _build_lazy_loaders(info: MOInfo, token: Token, arguments: dict) -> dict:
    """Loaders for the lazy CEL variables, memoized for this permission check.

    Each returns an awaitable computing its value at most once (an ``actor`` or
    ``current`` referenced by several candidate rules is resolved a single time).
    """
    cache: dict[str, Any] = {}

    async def actor() -> Any:
        if "actor" not in cache:
            cache["actor"] = await _resolve_actor(info, token)
        return cache["actor"]

    async def current() -> Any:
        if "current" not in cache:
            cache["current"] = await _load_current(info, arguments)
        return cache["current"]

    return {"actor": actor, "current": current}


async def _check_spec_passes(info: MOInfo, spec: dict) -> bool:
    """Whether one check-spec's SQL existence check passes.

    A check-spec is ``{collection, filter, check?, field?}``: ``check`` defaults
    to ``"IN"`` (require an object matching ``filter`` whose id equals ``field``);
    ``"EXISTS"`` requires only that *some* object matches ``filter``. A malformed
    spec raises :class:`EntityFilterError` (fail hard). An ``IN`` with a null
    ``field`` cannot match (an absent target denies), so returns ``False``.
    """
    collection = spec.get("collection")
    if not isinstance(collection, str):
        raise EntityFilterError(f"check-spec missing a string 'collection': {spec!r}")
    entity_spec = _entity_filter_spec(collection)

    filter_map = spec.get("filter", {})
    if not isinstance(filter_map, dict):
        raise EntityFilterError(
            f"check-spec 'filter' must be a map, got {type(filter_map).__name__}"
        )
    try:
        entity_filter = entity_spec.from_dict(filter_map)
    except ValueError as exc:
        raise EntityFilterError(str(exc)) from exc

    predicate = entity_spec.predicate(info, entity_filter)

    check = spec.get("check", "IN")
    if check == "IN":
        field = spec.get("field")
        if field is None:
            # `IN` pins the object by uuid; without one there is nothing to grant.
            return False
        try:
            field_uuid = field if isinstance(field, UUID) else UUID(str(field))
        except (ValueError, TypeError) as exc:
            raise EntityFilterError(
                f"check-spec 'field' is not a valid uuid: {field!r}"
            ) from exc
        predicate = and_(predicate, entity_spec.id_column == field_uuid)
    elif check != "EXISTS":
        raise EntityFilterError(f"check-spec has unknown check kind {check!r}")

    session: AsyncSession = info.context.session
    return bool(await session.scalar(select(exists().where(predicate))))


async def _entity_filter_grants(
    info: MOInfo,
    token: Token,
    arguments: dict | None,
    filter_value: str,
    loaders: dict,
) -> bool:
    """Whether a rule's ``filter`` grants access to the object being accessed.

    ``filter_value`` is a CEL expression evaluated with ``token``/``input`` (and,
    lazily, ``actor``/``current``) in scope; it returns one or more check-specs,
    each a SQL existence check (see :func:`_check_spec_passes`). The rule grants
    only when **all** of them pass (AND); OR is expressed across a policy's rules.

    Returns ``False`` only when the check-specs were evaluated and one genuinely
    does not match. Anything that prevents evaluation raises
    :class:`EntityFilterError` (fail hard) rather than returning ``False``, so a
    misconfigured rule cannot masquerade as a deny.
    """
    if not arguments:  # pragma: no cover - mutators always pass their arguments
        raise EntityFilterError("entity filter but no field arguments to match against")
    base_vars = build_filter_base_vars(token, _input_map(arguments))
    try:
        specs = await evaluate_filter(filter_value, base_vars, loaders)
    except ValueError as exc:
        raise EntityFilterError(str(exc)) from exc
    # A filter that yields no check-specs grants nothing: there is no ownership
    # basis to satisfy, so denying is the fail-closed choice. It also matches
    # legacy ``check_owner`` (an empty entity set denies), e.g. a bulk mutator
    # invoked with an empty input list (``input.map`` over ``[]``).
    if not specs:
        return False
    for spec in specs:
        if not await _check_spec_passes(info, spec):
            return False
    return True


async def _applicable_rule_index(
    info: MOInfo, token: Token
) -> dict[tuple[str, str], list[tuple[str | None, str | None]]]:
    """The rules of the caller's active policies, cached per request.

    Every field resolve consults the policy engine, so the applicable rules --
    the rules of the active policies whose actor matches the caller -- are
    fetched once and cached on the request context, keyed by their
    ``(type, field)`` for O(1) candidate lookup. The caller (roles) is constant
    within a request, so the set is too; this turns a query that resolves many
    fields into a single policy query.
    """
    context = info.context
    if context.applicable_policy_rules is None:
        actor_filter = actor_filter_for(token.realm_access.roles)
        predicate = policy_predicate(PolicyFilter(activated=True, actor=actor_filter))
        query = (
            select(
                db.PolicyRule.type,
                db.PolicyRule.field,
                db.PolicyRule.condition,
                db.PolicyRule.filter,
            )
            .where(db.PolicyRule.policy_fk == db.Policy.id)
            .where(predicate)
        )
        session: AsyncSession = context.session
        index: dict[tuple[str, str], list[tuple[str | None, str | None]]] = {}
        for rule_type, rule_field, condition, filter in (
            await session.execute(query)
        ).all():
            index.setdefault((rule_type, rule_field), []).append((condition, filter))
        context.applicable_policy_rules = index
    return context.applicable_policy_rules


async def actor_grants_field(
    info: MOInfo,
    token: Token,
    type: str,
    field: str,
    arguments: dict | None = None,
) -> bool:
    """Whether the calling actor may access the GraphQL ``(type, field)``.

    True if the actor has an active policy that applies to them (by role) and
    has a rule granting the ``(type, field)`` -- where either component may be
    the wildcard ``"*"`` -- whose CEL condition (if any) holds *and* whose
    entity filter (if any) matches the object being accessed. This is the core
    of the policy-based access control (PBAC) permission engine.

    ``arguments`` (the resolver's field arguments) are used to evaluate a rule's
    entity ``filter``; each check-spec the filter returns names the collection it
    targets, so the collection does not have to be derived from ``field``.

    The applicable rules are fetched once per request (see
    :func:`_applicable_rule_index`); the candidates for this ``(type, field)``
    are then checked in Python: each rule's condition (if any) must hold and its
    entity filter (if any) must match. A rule with neither grants outright.
    """
    index = await _applicable_rule_index(info, token)
    # Candidate rules match this exact (type, field) or a wildcard in either
    # component (``type IN (type,'*') AND field IN (field,'*')``).
    rules = (
        index.get((type, field), [])
        + index.get((type, "*"), [])
        + index.get(("*", field), [])
        + index.get(("*", "*"), [])
    )
    if not rules:
        return False
    # Access is granted if any candidate rule is satisfied: its CEL condition
    # (if any) holds and its entity filter (if any) matches. The condition
    # activation and the lazy filter loaders are built once and reused across
    # rules (so e.g. `actor` is resolved at most once per check).
    activation = None
    loaders = None
    for condition, filter in rules:
        if condition is not None:
            if activation is None:
                activation = build_activation(token)
            if not evaluate_condition(condition, activation):
                continue
        if filter is not None:
            if loaders is None:
                loaders = _build_lazy_loaders(info, token, arguments or {})
            if not await _entity_filter_grants(info, token, arguments, filter, loaders):
                continue
        return True
    return False
