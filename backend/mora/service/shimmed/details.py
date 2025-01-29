# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from fastapi import Body
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from more_itertools import first
from more_itertools import one
from ramodels.mo.detail import DetailTermination

from mora import mapping
from mora.auth.keycloak import oidc
from mora.graphapi.shim import execute_graphql
from mora.service import handlers
from mora.service.detail_writing import router as details_router

from .errors import handle_gql_error

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


@details_router.get(
    "/e/{id}/details/",
    responses={
        "400": {"description": "Invalid input"},
        "404": {"description": "No such endpoint"},
    },
)
async def list_employee_details(id: UUID) -> dict[str, bool]:
    """List the available 'detail' types under this employee.

    Return:
        A dictionary akin to:

        {
            "address": false,
            "association": false,
            "engagement": true,
            "it": false,
            "leave": true,
            "manager": false,
            "role": false
        }

        Where if value is true, it informs you that at least one entry exists for the
        corresponding key, either in the past, present or future.
    """
    # XXX: You may be tempted to optimize this by adding limits to the subqueries.
    #
    #      This temptation may have overtaken a lesser man, but not you!
    #      You will never be tempted beyond what you can bear! You will endure it!
    #
    #      For you, you realize the consequences of bitemporal consolidation!
    #      You foresee that objects may exist even if the first is unseeable!
    #      You will stand against temptation and the evils of LoRa!
    #      Resist the evils of LoRa! CONSTANT VIGILANCE! Conquer it!
    #
    #      You will succeed and conquer it using your vast intelligence!
    #      Your spirit is strong, even when the flesh is weak!
    #      Your perseverance is inspiring!
    #
    #      Blessed are the ones who perseveres under trial!
    #      You have stood the test of LoRa and won against its evils!
    query = """
        query GetEmployeeDetails($uuid: UUID!) {
          employees(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
            objects {
              objects {
                address: addresses(filter: {from_date: null, to_date: null}) {
                  uuid
                }
                association: associations(filter: {from_date: null, to_date: null}) {
                  uuid
                }
                engagement: engagements(filter: {from_date: null, to_date: null}) {
                  uuid
                }
                it: itusers(filter: {from_date: null, to_date: null}) {
                  uuid
                }
                leave: leaves(filter: {from_date: null, to_date: null}) {
                  uuid
                }
                manager: manager_roles(filter: {from_date: null, to_date: null}) {
                  uuid
                }
              }
            }
          }
        }
    """
    variables = {"uuid": id}
    # Execute GraphQL query to fetch required data
    response = await execute_graphql(
        query,
        variable_values=jsonable_encoder(variables),
    )
    handle_gql_error(response)
    validities = one(response.data["employees"]["objects"])["objects"]
    return {
        **{
            key: any(employee[key] for employee in validities)
            for key in first(validities).keys()
        },
        "kle": False,
        "org_unit": False,
        "owner": False,
        "related_unit": False,
    }


@details_router.get(
    "/ou/{id}/details/",
    responses={
        "400": {"description": "Invalid input"},
        "404": {"description": "No such endpoint"},
    },
)
async def list_org_unit_details(id: UUID) -> dict[str, bool]:
    """List the available 'detail' types under this organisation unit.

    Return:
        A dictionary akin to:

        {
            "address": false,
            "association": false,
            "engagement": true,
            "it": false,
            "leave": true,
            "manager": false,
            "role": false
        }

        Where if value is true, it informs you that at least one entry exists for the
        corresponding key, either in the past, present or future.
    """
    # XXX: You may be tempted to optimize this by adding limits to the subqueries.
    #
    #      This temptation may have overtaken a lesser man, but not you!
    #      You will never be tempted beyond what you can bear! You will endure it!
    #
    #      For you, you realize the consequences of bitemporal consolidation!
    #      You foresee that objects may exist even if the first is unseeable!
    #      You will stand against temptation and the evils of LoRa!
    #      Resist the evils of LoRa! CONSTANT VIGILANCE! Conquer it!
    #
    #      You will succeed and conquer it using your vast intelligence!
    #      Your spirit is strong, even when the flesh is weak!
    #      Your perseverance is inspiring!
    #
    #      Blessed are the ones who perseveres under trial!
    #      You have stood the test of LoRa and won against its evils!
    query = """
        query GetOrganisationUnitDetails($uuid: UUID!) {
          org_units(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
            objects {
              objects {
                address: addresses(filter: {from_date: null, to_date: null}) {
                  uuid
                }
                association: associations(filter: {from_date: null, to_date: null}) {
                  uuid
                }
                engagement: engagements(filter: {from_date: null, to_date: null}) {
                  uuid
                }
                it: itusers(filter: {from_date: null, to_date: null}) {
                  uuid
                }
                kle: kles(filter: {from_date: null, to_date: null}) {
                  uuid
                }
                leave: leaves(filter: {from_date: null, to_date: null}) {
                  uuid
                }
                manager: managers {
                  uuid
                }
                owner: owners {
                  uuid
                }
                related_unit: related_units(filter: {from_date: null, to_date: null}) {
                  uuid
                }
              }
            }
          }
        }
    """
    variables = {"uuid": id}
    # Execute GraphQL query to fetch required data
    response = await execute_graphql(
        query,
        variable_values=jsonable_encoder(variables),
    )
    handle_gql_error(response)
    validities = one(response.data["org_units"]["objects"])["objects"]
    return {
        **{
            key: any(org_unit[key] for org_unit in validities)
            for key in first(validities).keys()
        },
        "org_unit": True,
    }
