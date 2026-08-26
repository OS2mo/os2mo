# Coverage: the `# pragma: no cover` mystery

An investigation into code that was excluded from coverage with
`# pragma: no cover` (and historically with `# coverage: pause` /
`# coverage: unpause` block markers), where it was assumed that the code was
*covered but not counted* by coverage.

**TL;DR: There is no coverage under-reporting bug. The pragmas are hiding
genuinely dead code. The fix is to delete the dead code (and the useless
`concurrency` setting), not to keep the pragmas.**

## History of the markers

The "custom pragma start/stop" markers were `# coverage: pause` …
`# coverage: unpause` blocks, removed and reintroduced as line-level
`# pragma: no cover` in:

- `93219d35e` — *remove all `pragma: no cover` and `coverage: pause/unpause`*.
  This also deleted a custom `exclude_also` regex from `pyproject.toml`:
  `'coverage: pause(?s:.)*?coverage: unpause'`.
- `99f22fb9c` — *reintroduce `pragma: no cover`, now without
  `coverage: pause/unpause`*.

The two components where a *block* (pause…unpause) was collapsed into line
pragmas:

1. `mora/service/orgunit.py` — `OrgUnitRequestHandler.submit()`.
2. `mora/service/shimmed/details.py` — `_termination_request_handler()`.

## What removing the pragmas revealed

Running the termination tests with the pragmas stripped from
`mora/service/shimmed/details.py`:

- **Lines 70-71** (`handler = grapql_terminate_handlers.get(...)` /
  `return await handler(...)`) show as **missing — and are genuinely dead
  code.** `GRAPHQL_COMPATIBLE_TYPES` has its only entry commented out, so the
  `if detail_termination.type not in {}.keys()` check is always true and the
  function always returns at `return uuids[0]`.
- **Lines 43-44** (`if not results: return ""`): the pragma was hiding partial
  coverage — the `if` executes but `return ""` never does (every test passes a
  non-empty payload, and `results[0]` short-circuits).

## Why it looked like a coverage bug (but isn't)

`mora/handler/impl/address.py` lines 60-88 (the legacy REST read path) were
pragma'd. With the pragmas stripped, running the legacy REST address tests
reported lines 60-88 as **missing**, even though the tests pass and return
full data. That looked exactly like "covered but not counted".

Instrumentation disproved it:

- A debug write injected at line 60 **never fired** during
  `tests/test_integration_address.py::test_reading`.
- A probe at the function entry showed `is_graphql()` returns **`True`** for
  these REST endpoint tests, because the REST
  `/service/.../details/address` endpoint internally calls `execute_graphql`,
  which sets the `is_graphql` context variable. The function therefore returns
  early at lines 46-59, and lines 60-88 are **never executed**.

The earlier "100% with pragmas" was pure pragma-masking of dead code.

### The `concurrency` red herring

`pyproject.toml` sets:

```toml
[tool.coverage.run]
# coverage does not work properly with the mixed concurrency strategies of
# fastapi, strawberry and (async) sqlalchemy by default.
concurrency = ["greenlet", "thread"]
```

This is a no-op for asyncio code:

- asyncio does **not** use greenlets. A task runs on the *main* greenlet of a
  single thread (`greenlet.getcurrent()` inside a task *is* the main
  greenlet).
- Isolated repros of `asyncio.create_task` + `gather`, and of the FastAPI
  `TestClient`, all report **100%** correctly — plain task scheduling does not
  lose coverage.

## Minimal repro

`coverage_repro.py` (repo root) demonstrates the real phenomenon: dead code
hidden behind `# pragma: no cover`.

```bash
coverage run --source=coverage_repro coverage_repro.py
coverage report -m
```

- **WITH pragmas:** `100%` — the dead code is completely hidden.
- **WITHOUT pragmas** (strip the `# pragma: no cover` suffixes): `69%`,
  missing the legacy `graphql_style_handler` branch and the
  `terminate_handler` tail — the same kind of lines that are pragma'd in the
  real code (`address.py` 60-88, `details.py` 70-71).

## The solution

**Delete the dead code and the wrong `concurrency` setting — not the pragmas.**

1. **Remove the genuinely-dead legacy branches** instead of pragma'ing them:
   - `mora/handler/impl/address.py` 60-88 (and similar legacy
     `is_graphql() == False` branches in the other readers) — unreachable
     because all reads route through GraphQL.
   - `mora/service/shimmed/details.py` 70-71 — unreachable because
     `GRAPHQL_COMPATIBLE_TYPES` is empty; either implement the handlers or drop
     the tail.
   - `mora/service/shimmed/details.py` 43-44 (`if not results: return ""`) —
     the `return ""` is unreachable; simplify.

2. **Fix `pyproject.toml`**: `concurrency = ["greenlet", "thread"]` does
   nothing for asyncio and gives false confidence. Remove it (or stop
   expecting it to help).

3. **Keep `pragma: no cover` only for true defensive/unreachable code** (e.g.
   abstract-method `pass`, `AssertionError` guards), with a short comment
   stating *why* it is unreachable — so it isn't mistaken for masked dead code
   later.

The pragmas were never the disease; they were masking the symptom (dead
code). Removing the dead code makes the pragmas unnecessary and the coverage
report honest.
