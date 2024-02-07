# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from typing import Literal

from fastapi.encoders import jsonable_encoder
from fastramqpi.context import Context
from gql import gql
from pydantic import Extra
from pydantic import Field
from ramodels.mo._shared import JobFunction
from ramodels.mo._shared import MOBase
from ramodels.mo._shared import PersonRef
from ramodels.mo._shared import UUID


class CustomerSpecific(MOBase, extra=Extra.allow):  # type: ignore
    async def sync_to_mo(self, context: Context) -> list:
        return []

    async def sync_to_ldap(self):
        pass


class JobTitleFromADToMO(CustomerSpecific):
    user: PersonRef = Field(
        description=("Reference to the employee of the created engagement object.")
    )
    job_function: JobFunction | None = Field(
        description=(
            "Reference to the job function class for the created engagement object."
        ),
        default=None,
    )
    job_function_fallback: JobFunction = Field(
        description=(
            "Reference to the job function class for the created engagement object."
        )
    )
    type_: Literal["jobtitlefromadtomo"] = Field(
        "jobtitlefromadtomo", alias="type", description="The object type."
    )

    @classmethod
    def from_simplified_fields(
        cls,
        user_uuid: UUID,
        job_function_uuid: UUID | None,
        job_function_fallback_uuid: UUID,
        **kwargs
    ) -> "JobTitleFromADToMO":
        """Create an jobtitlefromadtomo from simplified fields."""
        user = PersonRef(uuid=user_uuid)
        job_function = JobFunction(uuid=job_function_uuid)
        job_function_fallback = JobFunction(uuid=job_function_fallback_uuid)
        return cls(
            user=user,
            job_function=job_function,
            job_function_fallback=job_function_fallback,
            **kwargs
        )

    async def sync_to_mo(self, context: Context):
        async def get_engagement_details(gql_session, employee_uuid):
            query = gql(
                """
            query GetEngagementUuids($employees: [UUID!]) {
              engagements(employees: $employees) {
                objects {
                  current {
                    uuid
                    validity {
                      from
                      to
                    }
                  }
                }
              }
            }
            """
            )
            result = await gql_session.execute(
                query,
                variable_values=jsonable_encoder(
                    {
                        "employees": employee_uuid,
                    }
                ),
            )

            return [
                {
                    "uuid": res["current"]["uuid"],
                    "from": res["current"]["validity"]["from"],
                    "to": res["current"]["validity"]["to"],
                }
                for res in result["engagements"]["objects"]
            ]

        async def set_job_title(engagement_details: list):
            query = gql(
                """
            mutation SetJobtitle($uuid: UUID!,
                                 $from: DateTime!,
                                 $to: DateTime,
                                 $job_function: UUID) {
              engagement_update(
                input: {uuid: $uuid,
                        validity: {from: $from, to: $to},
                        job_function: $job_function}
              ) {
                uuid
              }
            }
            """
            )
            jobs = []
            job_func = self.job_function_fallback.uuid
            if self.job_function is not None:
                job_func = self.job_function.uuid
            # obj is the dict sent from get engagements
            for obj in engagement_details:
                jobs.append(
                    {
                        "uuid_to_ignore": obj["uuid"],
                        "document": query,
                        "variable_values": jsonable_encoder(
                            {"job_function": job_func, **obj}
                        ),
                    }
                )
            return jobs

        engagement_details = await get_engagement_details(
            gql_session=context["legacy_graphql_session"],
            employee_uuid=self.user.uuid,
        )
        return await set_job_title(engagement_details=engagement_details)
