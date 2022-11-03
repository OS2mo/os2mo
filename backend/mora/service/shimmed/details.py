# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from fastapi import Body
from fastapi import Depends

from mora import mapping
from mora.auth.keycloak import oidc
from mora.service import handlers
from mora.service.detail_writing import router as details_router
from ramodels.mo.detail import DetailTermination

# Handlers of ramodels.mo.detail.Detail-types we have GraphQL mutators for
GRAPHQL_COMPATIBLE_TYPES = {
    # mapping.RequestType.TERMINATE: {
    #     mapping.ADDRESS: lambda dt: _address_terminate_graphql_handler(dt),
    # }
}


@details_router.post(
    "/details/terminate", responses={"400": {"description": "Unknown role type"}}
)
async def terminate(
    reqs: list[DetailTermination] | DetailTermination = Body(...),
    permissions=Depends(oidc.rbac_owner),
):
    results: list[str] = []
    for req in [reqs] if not isinstance(reqs, list) else reqs:
        results.append(await _termination_request_handler(req))

    # Format response to be compatible with legacy interactions
    if isinstance(reqs, list):
        return results

    if not results:
        return ""

    return results if len(results) > 1 else results[0]


# Private methods


async def _termination_request_handler(detail_termination: DetailTermination) -> str:
    """Tries to find a GraphQL mutation handler for the detail-termination, or defaults
    to legacy implementation."""

    grapql_terminate_handlers = GRAPHQL_COMPATIBLE_TYPES.get(
        mapping.RequestType.TERMINATE, {}
    )

    # LEGACY implementation for details missing GraphQL mutators (uses: .to_dict())
    if detail_termination.type not in grapql_terminate_handlers.keys():
        legacy_requests = await handlers.generate_requests(
            [detail_termination.to_dict()], mapping.RequestType.TERMINATE
        )

        uuids = await handlers.submit_requests(legacy_requests)
        return uuids[0]

    # Find the GraphQL mutation handler and return it for the request
    handler = grapql_terminate_handlers.get(detail_termination.type)
    return await handler(detail_termination)
