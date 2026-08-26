# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Minimal repro: dead code hidden behind `# pragma: no cover`.

This demonstrates the actual issue found in os2mo's coverage: code excluded
with `# pragma: no cover` that is *genuinely never executed* (dead code),
not code that is executed but under-reported by coverage.

Run:
    coverage run --source=coverage_repro -m coverage_repro
    coverage report -m

Expected: the pragma'd-but-reachable line shows as covered once the pragma is
removed, while the pragma'd-and-dead branch shows as missing -- proving the
pragmas were masking dead code, not a coverage under-reporting bug.
"""


def graphql_style_handler(is_graphql: bool) -> dict:
    """Mimics AddressReader._get_mo_object_from_effect.

    The modern path returns early (is_graphql=True). The legacy path below is
    dead code: callers always go through execute_graphql, so is_graphql is
    always True. Yet the legacy lines carry `# pragma: no cover`, hiding that
    they are never executed.
    """
    if is_graphql:
        return {"value": "modern"}  # covered

    legacy = {"value": "legacy"}  # pragma: no cover  <- dead, hidden by pragma
    return legacy  # pragma: no cover                 <- dead, hidden by pragma


def terminate_handler(graphql_handlers: dict, req_type: str) -> str:
    """Mimics shimmed/details._termination_request_handler.

    GRAPHQL_COMPATIBLE_TYPES is empty (everything commented out), so the
    `req_type not in handlers` branch is always taken and the tail is dead.
    """
    if req_type not in graphql_handlers:
        return "legacy-uuid"  # covered

    handler = graphql_handlers.get(req_type)  # pragma: no cover  <- dead
    return handler(req_type)  # pragma: no cover                  <- dead


if __name__ == "__main__":
    # Both callers exercise only the modern/legacy-early-return paths.
    assert graphql_style_handler(is_graphql=True) == {"value": "modern"}
    assert terminate_handler({}, "address") == "legacy-uuid"
