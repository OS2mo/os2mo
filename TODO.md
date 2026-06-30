# Reimplement `owner` authorization as data-driven PBAC policies

This is a **self-contained implementation spec**. It assumes no prior context.
All paths are relative to the `os2mo/` project root unless noted. Every design
decision is pinned and the code facts have been verified (§0).

## 0. Verified facts (confirmed against the code)
- **`current` shape (§4.3) — DECIDED (minimal, intentionally revisitable):**
  expose only what move needs — `{"parent": <uuid str|null>}` for org-unit, mapped
  from the LoRa object (do NOT pass the raw LoRa registrering through), so
  `current.parent` is a uuid string comparable to `input.parent`. Cheap to change
  later (local loader swap, no engine impact).
- **Owner predicate (§4.4) — VERIFIED, template already exists.** Owner
  org-functions are marked by `OrganisationFunktionAttrEgenskaber.funktionsnavn ==
  "owner"` (`mapping.OWNER`, `mora/mapping.py:128`). Relation kinds (enum
  `OrganisationFunktionRelationKode` in `mora/db/_organisationsfunktion.py:63`):
  `tilknyttedebrugere` = owned employee, `tilknyttedeenheder` = owned org-unit,
  `tilknyttedepersoner` = owner person. **`owner_predicate`
  (`mora/graphapi/resolvers.py:1687`) and `OwnerFilter.owner: EmployeeFilter`
  already implement the exact join we need** (in the opposite direction) — copy it.
- **Predicates + id-columns (§4.5) — VERIFIED, all 12 present, no scope cut.**
  Every collection has a clean `(info, filter) -> ColumnElement` predicate; exact
  names and id-columns in §4.5.
- **UNKNOWN detection (§4.3) — VERIFIED.** An unbound declared var makes the
  **whole result** evaluate to an unknown (no recursive scan needed):
  `result.type() == cel.Type.ERROR` and `str(result.value())` starts with
  `'UNKNOWN: No value with name "<var>" found in Activation'`. The string is the
  reliable signal (it names the variable); `ERROR` alone is generic (also real
  errors). Branch-sensitive: an untaken branch referencing the var stays concrete.

---

## 1. Goal

Replace the bespoke `owner` authorization (the "owner" Keycloak role +
`check_owner`) with **data-driven policies** under `policy_rbac` mode.

A policy **rule** carries a **CEL expression** that returns one or more
*check-specs*; the engine runs each as a SQL existence check and grants access
when they all pass. Owner becomes a bootstrap policy (actor `role: owner`) whose
rules carry per-mutator CEL expressions encoding "you own the affected entity".

Behavior reproduces today's `check_owner` faithfully for create / update /
terminate / delete / org-unit move, for the **full set** of owner-protected
mutators across all collections (§6). Read-side row filtering is out of scope for
this task but is a planned future direction — see §11 (don't design anything that
precludes it).

**Mode note:** under `policy_rbac` the legacy role+`check_owner` branch in
`permissions.py` is never reached (the PBAC branch returns first). So the owner
policy *is* the owner mechanism in PBAC mode; the legacy `check_owner` stays
untouched and continues to serve non-PBAC mode. **Do not remove or change
`check_owner`, `owner.py`, or `uuid_extractor.py`.**

---

## 2. Current state of the codebase (already implemented — build on this)

A prior change added a generic per-collection "entity rule filter" to the PBAC
engine. This task **generalizes** it (and removes parts of it). Read this first.

### Policy engine
- `mora/db/policies.py` — `PolicyRule` ORM model: `pk, type, field,
  condition (str|None), filter (str|None), policy_fk`; unique constraint
  `uq_policy_rule` over `(policy_fk, type, field, condition, filter)` with
  `postgresql_nulls_not_distinct=True`. Migration that added `filter`:
  `alembic/versions/c1f2a3b4d5e6_add_policy_rule_filter.py`.
- `mora/graphapi/policies.py`:
  - `actor_grants_field(info, token, type, field, permission=None, collection=None,
    arguments=None) -> bool` — **the single PBAC entrypoint**. Selects the calling
    actor's currently-valid policies' rules matching `(type, field|"*")`; grants if
    any rule's `condition` (CEL bool, optional) holds AND its `filter` matches.
  - `_entity_filter_grants(info, token, collection, arguments, filter_value)`
    — current single-check impl (CEL → one filter map → `exists(predicate(filter)
    AND id_column == _target_uuid(arguments))`). **Rewritten in §4.2.**
  - `EntityFilterSpec` dataclass `{from_dict, predicate, id_column}`;
    `_entity_filter_spec(collection)` lazy registry (**currently only `ituser`**).
  - `split_rule_field`, `rule_field_supports_filter`, `RULE_OPERATIONS`,
    `FILTERABLE_OPERATIONS`, `ENTITY_FILTER_COLLECTIONS`, `_target_uuid`,
    `validate_rule_filter`, `_input_map`, `_person_filter_from_dict`,
    `deserialize_person_filter`, `_ituser_filter_from_dict`, `EntityFilterError`.
    Several of these are **removed/changed** — see §8.
  - `_input_map(arguments) -> dict` — exposes the mutator argument to CEL as
    `input` via `jsonable_encoder(source, custom_encoder={UNSET_TYPE: lambda _:
    None})`. Input-style mutators: `source = arguments["input"]`; bare-arg mutators
    (delete): `source = arguments` (so `input.uuid` works). **Keep.**
  - `person_filter` actor kind (separate feature, **leave as-is**): a
    `PolicyActor` of kind `person_filter` stores JSON `EmployeeFilter`; matches if
    `token.uuid ∈ employee_predicate(filter)`. Stays static (there's a TODO there
    about CEL — out of scope).
- `mora/graphapi/policy_cel.py`:
  - `_VARIABLES = {"token": DYN, "permission": DYN, "input": DYN}`;
    `_ENV = cel.NewEnv(variables=_VARIABLES)`; `_compile` (lru_cached).
  - `validate_condition`, `validate_filter` (compile-check, raise ValueError).
  - `build_activation(token, permission)`; `build_filter_activation(token, input,
    permission=None)`; `_token_context(token) -> {"uuid","preferred_username","roles"}`.
  - `evaluate_condition -> bool`; `evaluate_filter(expr, activation) -> dict`
    (uses `_to_native`); `_to_native(value)` recursively unwraps CEL values
    (nested maps are `_CelMapItemAccessor` wrappers exposing `.value()`).
- `mora/graphapi/permissions.py` — PBAC branch calls
  `actor_grants_field(info, token, parent_type.name, field_name, permission_role,
  collection=collection, arguments=kwargs)`. `collection`/`permission_type` come
  from `gen_permission(collection, permission_type)`; `kwargs` holds the mutator
  args. **Change: stop passing `collection`; keep `arguments=kwargs`.**
- `mora/graphapi/mutators.py` — `_declare_policy_rule(... condition, filter)`,
  `policy_rule_declare`, `policy_rules_declare` thread `filter` and call
  `validate_rule_filter`. `mora/graphapi/inputs.py` — `PolicyRule*Input.filter`.
- Tests: `tests/test_policies.py` (integration; `graphapi_post`, `empty_db`,
  `set_auth`, `set_settings`, `root_org`, `another_transaction`). Existing
  rule-filter tests use bare filter-map CEL matched against the object uuid —
  **migrate to the check-spec format (§4.1).**

### CEL library facts (verified — `from cel_expr_python import cel`)
- Map literals are valid CEL; `.value()` returns a Python dict but **nested levels
  need recursive unwrap** (`_to_native`).
- A variable **declared in the env but not bound in the activation** does NOT
  raise: eval yields an UNKNOWN `Value` (`.value()` == `'UNKNOWN: No value with
  name "X" found in Activation'`) that **propagates** and is **branch-sensitive**
  (`cond ? a : current.x` stays concrete if that branch isn't taken). The `Value`
  has `.type` and `.plain_value`; detect UNKNOWN via `.type` (confirm the exact
  sentinel at implement time) with a `"UNKNOWN:"`-substring fallback.

---

## 3. How `owner` works today (reproduce faithfully)

- `mora/auth/keycloak/rbac.py`:
  - `check_owner(token, entities)` — `user_uuid = await _get_employee_uuid(token)`;
    for each `(EntityType, uuid)` compute `get_owners`; **grant iff `user_uuid` ∈
    owners for ALL entities** (empty entity set ⇒ deny).
  - `_get_employee_uuid(token)` — **default returns `token.uuid`**; if
    `settings.keycloak_rbac_authoritative_it_system_for_owners` is set, resolves
    the employee via an IT-system lookup (token.uuid ≠ employee uuid).
- `mora/auth/keycloak/owner.py`:
  - `get_owners(uuid, ORG_UNIT)` → `get_ancestor_owners(uuid)` — **hierarchical**:
    owners of the unit AND all ancestors ("every node is its own ancestor").
  - `get_owners(uuid, EMPLOYEE)` → `_get_entity_owners(uuid, EMPLOYEE)` — **direct
    only** (no hierarchy); reads owner org-functions on the employee via
    `OwnerReader.get_from_type(c, "e", uuid)`.
- Ownership = "owner" org-functions (function name `mapping.OWNER`). Relations
  (see `mora/mapping.py` OWNER_FIELDS, `mora/handler/impl/owner.py` `OwnerReader`,
  `mora/service/owner.py`): `tilknyttedepersoner` = **owner person**,
  `tilknyttedebrugere` = **owned employee**, `tilknyttedeenheder` = **owned org
  unit**.
- `mora/auth/keycloak/uuid_extractor.py` `get_entities_graphql` decides which
  entities are checked: create org_unit → `input.parent`; create employee →
  `input.uuid` (new uuid ⇒ no owners ⇒ deny); update org_unit → the unit + the new
  parent only if changed (the move case, compared via a DB read); details →
  prefer org-unit then person, over both the existing DB object and the input.

### Verified structural invariants (make the policy exact — see §6)
From `mora/graphapi/models.py` Create models:
- `EngagementCreate.org_unit`, `AssociationCreate.org_unit`, `KLECreate.org_unit`
  are **required**; `ManagerCreate.org_unit` required (`person` optional). ⇒
  org-unit always present.
- `LeaveCreate.person` required, no org_unit. ⇒ person-only.
- `RoleBindingCreate.org_unit: UUID | None`, `ituser` required, **no person**. ⇒
  org-unit-or-deny.
- `AddressCreate` / `ITUserCreate` enforce **exactly one of person/org_unit**
  (root_validators). ⇒ mutually exclusive.

**Consequence:** no object has both a person and an org-unit with the org-unit
*optional*. So `check_owner`'s "prefer org-unit, short-circuit" never has to choose
between two present links, and per-mutator hardcoded rules reproduce it exactly
**with no prefer-logic and no `current` for prefer**.

---

## 4. Target design

### 4.1 Rule filter = CEL returning check-spec(s)
A rule's `filter` is a **CEL expression** returning **one check-spec or a list of
them** (a single map is normalized to a one-element list). Each check-spec:

```
{ "collection": "employee" | "org_unit" | "ituser" | ...,  # which EntityFilterSpec
  "filter":     { ...MO filter map... },                    # constraint for that collection
  "check":      "IN" | "EXISTS",                            # optional; default "IN"
  "field":      <uuid> }                                    # REQUIRED when check == "IN"
```

CEL context: `token` (`{uuid, preferred_username, roles}`), `input` (mutator
argument map), `actor` (resolved caller employee uuid, lazy — §4.3), `current`
(existing DB object, lazy — §4.3), `permission`.

**No bare-map shorthand** — check-specs are the only accepted shape. Migrate the
existing `ituser` rule-filter tests to this format.

### 4.2 Engine evaluation (rewrite `_entity_filter_grants`)
For a rule with a non-null `filter`:
1. Evaluate the CEL (§4.3 handles lazy vars) → normalize the result to a **list**
   of check-specs.
2. For each check-spec: `spec = _entity_filter_spec(check["collection"])` (raise
   `EntityFilterError` if unknown); `f = spec.from_dict(check["filter"])`; then:
   - `check.get("check","IN") == "IN"`: `field = check["field"]`; require
     `exists(select 1 where spec.predicate(info, f) AND spec.id_column == field)`.
     `field` null ⇒ no match ⇒ check fails (correct: absent target denies). **`IN`
     auto-pins, so the filter is pure constraint and cannot over-grant.**
   - `== "EXISTS"`: require `exists(select 1 where spec.predicate(info, f))`.
     **Unpinned — grants on existence of ANY match; owner never uses it. Reserve
     for deliberate "is there any such row" semantics.**
3. The rule's filter passes iff **ALL** check-specs pass (AND). OR is across rules
   (a policy grants if any rule's `condition` + filter pass).
4. Any inability to evaluate (unknown collection, missing `field` for `IN`,
   malformed check-spec/filter, CEL compile/eval failure, non-map/list result) ⇒
   **raise (fail hard), never silently deny.** Keep `EntityFilterError`.

`field`/`collection` now come from the check-spec, so `_target_uuid` and the
`collection` argument to `actor_grants_field`/`_entity_filter_grants` are removed
(§8). `arguments` (kwargs) stays — needed for `input`/`current`.

### 4.3 Lazy CEL context (`actor`, `current`) via UNKNOWN-resolution
Both `actor` (resolved caller uuid; an async lookup in the IT-system config) and
`current` (an async DB read) are expensive and usually unused, so resolve them
lazily with one shared mechanism:
1. **Declare `actor` and `current` in `_VARIABLES`** (else referencing them is a
   *compile* error). Do not bind them by default.
2. Maintain a loader registry, e.g.
   `LAZY = {"actor": lambda: _resolve_actor(info, token),
            "current": lambda: _load_current(info, collection, arguments)}`
   (each returns an awaitable; values memoized on `info.context`).
3. Evaluate with `token`+`input` bound. An unbound declared var makes the **whole
   result** unknown (verified — no recursive scan needed): check the top-level
   result with `result.type() == cel.Type.ERROR` **and** `str(result.value())`
   starting with `'UNKNOWN: No value with name "'` — extract `<var>` from that
   string (it names the missing variable). A `cel.Type.ERROR` result whose value is
   NOT that `UNKNOWN: No value with name` string is a **genuine eval error → fail
   hard** (do not treat as a missing var).
4. For the named lazy var, `await` its loader, bind it, and **re-evaluate**. Repeat
   until the result is no longer an unknown or no progress (bounded by the number of
   lazy vars, ≤2 rounds). Branch-sensitive: a var is loaded only when the executed
   path dereferences it (an untaken branch referencing it stays concrete).
- `_resolve_actor(info, token)`: `await _get_employee_uuid(token)` (default ≈
  `token.uuid`, no DB; IT-system config does the lookup) → return its `str`. Owner
  rules reference `actor` so faithfulness holds in both configs.
- `_load_current(info, collection, arguments)`: load the existing object by
  `(collection, input.uuid)` and expose it as a CEL-friendly map (so `current.parent`
  works). Reuse `uuid_extractor._get_org_unit`/`_get_org_function` or the GraphQL
  resolver, then `jsonable_encoder` it. Create has no `current` (don't reference it
  in create rules).

### 4.4 The `owner` relation filter (the one new filter capability)
In `mora/graphapi/filters.py`, add a nested relation filter:
- `EmployeeFilter.owner: EmployeeFilter | None` — employees whose **direct** owner
  (an "owner" org-function with `tilknyttedebrugere` = the employee and
  `tilknyttedepersoner` matching the sub-filter person) matches. So `{"owner":
  {"uuids": [X]}}` = employees directly owned by person `X`.
- `OrganisationUnitFilter.owner: EmployeeFilter | None` — org-units whose
  **direct** owner (`tilknyttedeenheder` = the unit, `tilknyttedepersoner`
  matching) matches. **Hierarchy is NOT baked in here** — compose with the existing
  `OrganisationUnitFilter.ancestor` filter: `{"ancestor": {"owner": {"uuids":
  [X]}}}` = units whose self-or-ancestor is directly owned by `X` =
  `get_ancestor_owners` semantics. No recursive CTE to write.
- Implementation (`mora/graphapi/resolvers.py`) — **VERIFIED recipe; copy the
  existing `owner_predicate` (line 1687), which already does this exact join in the
  opposite direction.** Wire `owner` into `employee_predicate` (line 972) and
  `organisation_unit_predicate` (line 1907) the same way they append other nested
  sub-filter predicates. The new predicate for `EmployeeFilter.owner` (analogous
  for org-unit via `tilknyttedeenheder` / `OrganisationEnhedRegistrering`):

  ```python
  # in employee_predicate, when filter.owner is not None:
  # employees that are the OWNED side (tilknyttedebrugere) of an "owner"
  # org-function whose OWNER person (tilknyttedepersoner) matches filter.owner
  owner_funcs = (                       # owner org-functions whose owner-person matches
      select(OrganisationFunktionRelation.organisationfunktion_registrering_id)
      .where(
          OrganisationFunktionRelation.rel_type
          == OrganisationFunktionRelationKode.tilknyttedepersoner,
          OrganisationFunktionRelation.rel_maal_uuid.in_(
              select(BrugerRegistrering.bruger_id).where(
                  employee_predicate(info, filter.owner)
              )
          ),
          _get_virkning_clause(OrganisationFunktionRelation, filter),
      )
  )
  predicates.append(
      BrugerRegistrering.bruger_id.in_(
          select(OrganisationFunktionRelation.rel_maal_uuid).where(
              OrganisationFunktionRelation.rel_type
              == OrganisationFunktionRelationKode.tilknyttedebrugere,
              OrganisationFunktionRelation.organisationfunktion_registrering_id.in_(
                  # restrict to funktionsnavn == "owner" AND owner-person matches
                  select(OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id)
                  .where(
                      OrganisationFunktionAttrEgenskaber.funktionsnavn == "owner",
                      _get_virkning_clause(OrganisationFunktionAttrEgenskaber, filter),
                  )
                  .where(OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id.in_(owner_funcs))
              ),
              _get_virkning_clause(OrganisationFunktionRelation, filter),
          )
      )
  )
  ```
  Adjust to the codebase's exact helper usage (`uuid_shortcircuit`,
  `_get_virkning_clause`) by reading `owner_predicate`/`it_user_predicate`. Marker
  `"owner"` = `mapping.OWNER`. Enum members are on `OrganisationFunktionRelationKode`
  (`mora/db/_organisationsfunktion.py`). For the org-unit variant, swap
  `tilknyttedebrugere`→`tilknyttedeenheder` and match
  `OrganisationEnhedRegistrering.organisationenhed_id`.

### 4.5 Per-collection deserializers + registry coverage
**Explicit per-collection deserializers — dumb and predictable, no
type-introspection magic.** Each is a small function `_<x>_filter_from_dict(data:
dict) -> <FilterType>` modeled on the existing `_ituser_filter_from_dict` /
`_person_filter_from_dict`: read the known keys, coerce explicitly (`UUID(v)`,
`datetime.fromisoformat(v)`, `CPR(v)`, `[UUID(x) for x in ...]`), recurse into
nested sub-filters by calling the relevant `_*_from_dict`, and **preserve `UNSET`
for absent keys**. **Reject unknown keys with `ValueError`** (fail hard — never
silently drop a key an author wrote).

Each deserializer only needs to support the **subset of fields the policies
actually use**, not the whole filter type:
- `_person_filter_from_dict` (`EmployeeFilter`) — existing fields **plus a new
  `owner` key** → recurse `_person_filter_from_dict` (the owner is a person).
  Used for the `employee` collection and as the nested owner-person sub-filter.
- `_org_unit_filter_from_dict` (`OrganisationUnitFilter`) — keys `uuids`,
  `ancestor` → recurse `_org_unit_filter_from_dict`, `owner` → recurse
  `_person_filter_from_dict`. Used for the `org_unit` collection and the nested
  `org_unit` sub-filter.
- Object collections (`ituser`, `address`, `engagement`, `association`, `manager`,
  `leave`, `kle`, `rolebinding`, `related_unit`) — each only needs the
  `employee` and/or `org_unit` sub-filter keys its rules use (recurse
  `_person_filter_from_dict` / `_org_unit_filter_from_dict`). Because these are
  structurally identical, a single tiny **explicit** helper
  `_object_owner_filter_from_dict(filter_cls, data)` that handles exactly the keys
  `{"employee", "org_unit"}` (and rejects others) is acceptable — it is not the
  "smart generic"; it knows exactly two keys. Per-collection one-liners wrapping it
  are fine too.
- `deserialize_person_filter(value)` (the `person_filter` actor path) stays and
  uses `_person_filter_from_dict(json.loads(value))`.

`EntityFilterSpec` per collection = `{from_dict, predicate, id_column}`. Provide
specs for: `employee`, `org_unit`, `ituser`, `address`, `association`,
`engagement`, `leave`, `manager`, `owner`, `rolebinding`, `kle`, `related_unit`.
- `predicate` (all VERIFIED present in `resolvers.py`, signature `(info, filter)
  -> ColumnElement`): `employee` → `employee_predicate`; `org_unit` →
  `organisation_unit_predicate` (note the spelling); `ituser` →
  `it_user_predicate`; `address` → `address_predicate`; `association` →
  `association_predicate`; `engagement` → `engagement_predicate`; `leave` →
  `leave_predicate`; `manager` → `manager_predicate` (has an extra
  `inherit: bool = False` param — use the default); `owner` → `owner_predicate`;
  `rolebinding` → `rolebinding_predicate`; `kle` → `kle_predicate`;
  `related_unit` → `related_unit_predicate`.
- `id_column` (VERIFIED): employee → `BrugerRegistrering.bruger_id`; org_unit →
  `OrganisationEnhedRegistrering.organisationenhed_id`; all org-function
  collections (address, association, engagement, ituser, leave, manager, owner,
  rolebinding, kle, related_unit) →
  `OrganisationFunktionRegistrering.organisationfunktion_id`.

---

## 5. Caller identity (DECIDED: fully supported, no limitation)
Owner rules use the lazy `actor` var = `await _get_employee_uuid(token)` (§4.3),
which is faithful in **both** the default config (≈ `token.uuid`) and the
`keycloak_rbac_authoritative_it_system_for_owners` config (IT-system-resolved
employee uuid). Keep raw `token.uuid` available too for non-owner uses. (The lazy
machinery is shared with `current`, so this costs little.)

---

## 6. The bootstrap owner policy (per-mutator rules)
Seed via an alembic migration mirroring the existing policy-bootstrap migrations
under `alembic/versions/`. Policy: actor `role: owner`; one rule per protected
mutator, `condition` null, `filter` = the CEL below. **Cover the FULL set** — every
mutator `check_owner` guards today, across all collections in the table below
(create/update/terminate/delete + org-unit move). Generate the rule set
programmatically over the collection list rather than hand-writing each row.

Scope clarifications (pinned):
- "Full set" = the **owner-protected collections** in the table (those
  `get_entities_graphql` handles: employee, org_unit, address, association,
  engagement, ituser, leave, manager, owner, rolebinding, kle, related_unit). Do
  **not** add rules for collections owner never gated (class, facet, itsystem, org,
  configuration, rolebinding's `role`/itsystem types, etc.).
- **`refresh` is excluded** — it takes a `filter` (not an `input`), so today's
  owner path errors/denies it; omitting it is faithful.
- Give the policy a **well-known UUID** (for the migration's one-time idempotent
  insert). **Do NOT deletion-protect it** — it is a convenience **default starter**
  policy that customers are expected to customize or remove as they migrate to
  their own policies (treat like the `Administrator`/`Reader` bootstrap policies,
  NOT like the protected `policyadmin`). The migration **seeds it once** and must
  **not** recreate or "repair" it on later runs — respect a customer's edits or
  deletion.

Shorthand: `UNIT(field)` = `{"collection":"org_unit","check":"IN","field":field,
"filter":{"ancestor":{"owner":{"uuids":[actor]}}}}`; `PERSON(field)` =
`{"collection":"employee","check":"IN","field":field,"filter":{"owner":{"uuids":
[actor]}}}`. For update/terminate/delete, the check runs against the **object's own
collection** with the ownership **sub-filter**, pinned on `input.uuid` — e.g.
`{"collection":"ituser","check":"IN","field":input.uuid,"filter":{"org_unit":
{"ancestor":{"owner":{"uuids":[actor]}}}}}` (call this `OBJ_UNIT`) and the
`{"employee":{"owner":{"uuids":[actor]}}}` variant (`OBJ_PERSON`).

| Mutator(s) | Invariant | Rule(s) (CEL) |
|---|---|---|
| `engagement_*`, `association_*`, `kle_*`, `manager_*` (update/terminate/delete) | org-unit mandatory | one rule: `OBJ_UNIT` |
| `rolebinding_*` (update/terminate/delete) | org-unit nullable, no person | one rule: `OBJ_UNIT` (null org-unit ⇒ no match ⇒ deny, matches) |
| `leave_*` (update/terminate/delete) | person-only | one rule: `OBJ_PERSON` |
| `address_*`, `ituser_*` (update/terminate/delete) | exactly one of person/org-unit | **two rules** (OR): `OBJ_UNIT` and `OBJ_PERSON` (mutually exclusive ⇒ never double-grants) |
| `related_unit_*` (update/terminate/delete) | org-unit (origin) | one rule: `OBJ_UNIT` |
| `employee_update`, `employee_terminate` | — | one rule: `PERSON(input.uuid)` |
| `org_unit_terminate`, `org_unit_delete` | — | one rule: `UNIT(input.uuid)` |
| `org_unit_update` (move) | needs `current` | one rule returning a **list (AND)**: `[UNIT(input.uuid)] + (input.parent != null && input.parent != current.parent ? [UNIT(input.parent)] : [])` — note the `!= null` guard: an omitted/null `parent` is NOT a move (mirrors `check_owner`'s `if parent := getattr(input,'parent',None)`); only an explicitly-changed parent requires owning the new parent |
| `org_unit_create` | — | one rule: `UNIT(input.parent)` |
| detail `*_create` (address, ituser, engagement, association, leave, manager, kle, rolebinding, owner, related_unit) | — | one branching rule: `has(input.org_unit) ? UNIT(input.org_unit) : PERSON(input.person)` (org-unit-mandatory types reduce to `UNIT(input.org_unit)`; leave → `PERSON(input.person)`; related_unit → `UNIT(input.origin)`) |
| `employee_create` | — | one rule: `PERSON(input.uuid)` (no owners on a new uuid ⇒ deny, matches) |

Notes: create checks the input target (`field` = an `input.*`); update/terminate/
delete check the object (`field` = `input.uuid`) and the predicate joins to its
links. `manager.person` is optional but org-unit mandatory ⇒ always the org-unit
branch. Generate the migration's rule set programmatically over the collection
list to avoid hand-writing every row.

---

## 7. Faithfulness / known-equivalent edge cases
- Default & IT-system caller-identity: both faithful (§5).
- Prefer-org-unit: handled by the structural invariants (§3) — no special logic.
- address linked to an engagement (rare): no direct person/org-unit ⇒ `check_owner`
  denies; the rules yield no match ⇒ deny. Consistent.
- The owner policy only takes effect in `policy_rbac` mode (legacy `check_owner`
  serves non-PBAC mode unchanged).

---

## 8. Files to change (checklist)
- [ ] `mora/graphapi/policy_cel.py`: add `"actor"` and `"current"` to `_VARIABLES`;
  make `evaluate_filter` return a normalized **list** of check-specs; add the lazy
  resolution loop (UNKNOWN-detect → await loader → re-eval) and fold UNKNOWN-leaf
  detection into `_to_native`.
- [ ] `mora/graphapi/policies.py`: rewrite `_entity_filter_grants` as the check-spec
  interpreter (§4.2) with the lazy `actor`/`current` mechanism (§4.3); add
  `_resolve_actor` (`_get_employee_uuid`) and `_load_current`, memoized on
  `info.context`; replace `_entity_filter_spec` with the full registry (§4.5) using
  the generic `filter_from_dict`; **remove** `_target_uuid`,
  `rule_field_supports_filter`, `FILTERABLE_OPERATIONS`, `ENTITY_FILTER_COLLECTIONS`
  gating, and `split_rule_field` (unless still used elsewhere); drop the
  `collection` parameter from `actor_grants_field`. `validate_rule_filter` becomes
  **compile-check only** (any rule may carry a filter); keep `_input_map`.
- [ ] `mora/graphapi/policies.py`: add the per-collection deserializers (§4.5) —
  extend `_person_filter_from_dict` with an `owner` key, add
  `_org_unit_filter_from_dict`, and the object-collection deserializers (or the
  small explicit `_object_owner_filter_from_dict` helper); reject unknown keys;
  keep `deserialize_person_filter`.
- [ ] `mora/graphapi/filters.py`: add `owner: EmployeeFilter | None` to
  `EmployeeFilter` and `OrganisationUnitFilter`.
- [ ] `mora/graphapi/resolvers.py`: implement the `owner` relation predicate (join
  to `mapping.OWNER` org-functions) and wire it into `employee_predicate` and the
  org-unit predicate.
- [ ] `mora/graphapi/permissions.py`: drop `collection=` from the
  `actor_grants_field` call (keep `arguments=kwargs`).
- [ ] alembic migration: bootstrap the owner policy (actor `role: owner`, §6 rules).
- [ ] `mora/graphapi/mutators.py` / `inputs.py`: `validate_rule_filter` is
  compile-check only; no field/collection gating.
- [ ] Frontend `os2mo-naldo/web/src/lib/components/policies/PolicyFlow.svelte` +
  i18n: **remove the collection/operation gating** (`ruleSupportsFilter`,
  `SUPPORTED_FILTER_COLLECTIONS`, `FILTERABLE_OPERATIONS`); show the `filter` field
  as a free CEL textarea for **all rules**. Update `entity_filter_hint_suffix` /
  `policy_rule_filter_hint` (en + da) to describe "a CEL expression returning one or
  more access-check specs `{collection, filter, check, field}`".
- [ ] `tests/test_policies.py`: migrate existing rule-filter tests to check-specs;
  add owner tests (§9).

---

## 9. Verification / tests
Dev stack: `docker compose up --build --detach`. Run tests **only** via
`docker compose exec -T mo pytest tests/test_policies.py -k <expr> -p no:cacheprovider`
(never the whole suite; never bare `pytest`). Use `empty_db` + `root_org`;
`set_auth(user_uuid=..., preferred_username=...)`; then `set_settings(POLICY_RBAC=
"true", OS2MO_AUTH="true")`. Create people via `employee_create` (explicit `uuid`),
units via `create_org_unit`, owner relations via the owner mutator; use
`another_transaction()` for direct DB writes (e.g. corrupt a stored filter to
assert fail-hard). Set the actor's role to `owner` (so the bootstrap owner policy
applies).

Add integration tests proving end-to-end (as `role: owner`, PBAC mode):
- update/terminate/delete: owner of the linked person (or unit) may mutate;
  non-owner denied. Cover a person-linked (ituser/address), a unit-linked /
  org-unit-mandatory (engagement), an employee object, and an org-unit object.
- hierarchy: owning an ancestor org-unit grants editing a descendant unit and
  details under it (via `{"ancestor":{"owner":...}}`).
- create: may create under an owned parent/target; denied otherwise; `employee_create`
  denied for owner-only users.
- move (`org_unit_update`): owner of the unit + new parent may move; owning only
  the unit but not the new parent is denied (exercises the AND-list + `current`).
- lazy vars: a non-`current` rule does not load `current`; a non-owner filter rule
  does not resolve `actor`; both still work when referenced.
- fail hard: an unknown-collection / malformed check-spec surfaces an error, not a
  silent deny.

Quality gates: `docker compose exec -T -e RUFF_CACHE_DIR=/tmp/ruff mo ruff check
<files>` and `ruff format --diff`; `docker compose exec -T -e MYPY_CACHE_DIR=/tmp/mypy
mo mypy <files>` (fix only NEW errors; pre-existing errors exist in `policy_cel.py`);
frontend `docker compose exec -T -w /app naldo npx svelte-check --tsconfig ./tsconfig.json`.
Follow `os2mo/AGENTS.md`: `more_itertools` `one`/`only`/`first` over `[0]`;
integration tests, no mocks, `empty_db` over `fixture_db`; conventional commits with
a ticket number; no em-dashes; `pre-commit run --all-files` before committing.

---

## 10. Final engine model (summary)
**Grant ⟺ the calling actor has a currently-valid policy with a rule whose
`condition` (optional CEL bool) holds and whose `filter` (CEL → list of
check-specs) all pass.** Each check-spec `{collection, filter, check, field}` is a
SQL existence check: `IN` → `exists(predicate(filter) AND id == field)`; `EXISTS`
→ `exists(predicate(filter))`. AND across a rule's specs, OR across rules. CEL sees
`token`, `input`, and lazily `actor` (resolved caller uuid) and `current` (existing
object). Ownership uses the new `owner` relation filter (+ existing `ancestor` for
org-unit hierarchy). All per-mutator knowledge is data (the bootstrap owner
policy); the engine is a small generic interpreter; anything unevaluatable fails
hard. The owner policy is the PBAC-mode mechanism; legacy `check_owner` stays for
non-PBAC mode.

---

## 11. Future direction (NOT this task — don't preclude it)
Extend the same `{collection, filter}` mechanism to **read queries** as **row-level
filtering** (a deliberate, planned next step). Today a rule is a boolean gate on
`(type, field)`. For a *collection query* (e.g. `employees`, `itusers`), a policy
rule's filter should instead **restrict the returned rows** to those matching the
filter — i.e. the resolver `AND`s the policy filter's predicate into its query —
rather than allow/deny the whole field. This turns "owner" into "you may *read*
exactly the objects you own", and generalizes to any data-scoped read policy.

Design notes so nothing here blocks it:
- The check-spec already carries `{collection, filter}` and we already have the
  per-collection `EntityFilterSpec` (predicate + id_column). Row-level read
  filtering reuses **the same filter map and predicate** — the difference is the
  engine emits a **predicate to inject into the resolver**, not a boolean
  `exists()` check. So keep `filter`/predicate construction cleanly separable from
  the boolean `IN`/`EXISTS` evaluation, so a third "RESTRICT" mode can reuse it.
- It requires resolver-level integration (the collection resolvers must accept and
  `AND`-in a policy-derived predicate, OR-combined across the actor's applicable
  read policies, and default-deny when read policies exist but none match). That is
  a larger, separate change (touches every read resolver and the
  permission/resolver boundary) — out of scope now, but the engine + filter +
  per-collection predicate groundwork laid here is exactly its foundation.
- `IN`/`EXISTS` (this task) gate single operations; `RESTRICT` (future) scopes
  result sets. Same vocabulary, different application point.
