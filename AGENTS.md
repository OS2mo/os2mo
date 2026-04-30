# AGENTS Instructions

# Development Environment

- This project uses `docker compose` for the development environment.
- The development stack can be started using `docker compose up --build --detach`.

## Code Style

- Use `one`, `only` or `first` from `more_itertools` instead of `[0]`.

## Testing Instructions

- Write integration tests instead of unit tests, and avoid using mocks.
- Use fixtures from `backend/tests/conftest.py` when writing tests.
- Use the `empty_db` fixture, rather than the `fixture_db`.
- Never run `pytest` directly on the host.
- Always use `docker compose exec mo pytest backend/tests/...` to run tests.
  This requires starting the development environment first.
- Never run all tests; it takes too long. Only run relevant tests.

## Commit Instructions

- Branch names should include a ticket number, e.g. `69176-related-owner`.
- Make sure `pre-commit run --all-files` passes before committing.
- Commits must adhere to the conventional commits style and include a ticket
  number, e.g.:
  - `feat: [#68002] allow reading connected addresses through an engagement`.
  - `fix: [#68002] don't sleep when no events`.
