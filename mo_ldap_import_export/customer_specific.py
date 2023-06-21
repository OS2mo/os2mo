import datetime
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


class HolstebroEngagementUpdate(CustomerSpecific):
    user: PersonRef = Field(
        description=("Reference to the employee of the created engagement object.")
    )
    job_function: JobFunction = Field(
        description=(
            "Reference to the job function class for the created engagement object."
        )
    )
    type_: Literal["holstebroengagementupdate"] = Field(
        "holstebroengagementupdate", alias="type", description="The object type."
    )

    @classmethod
    def from_simplified_fields(
        cls, user_uuid: UUID, job_function_uuid: UUID, **kwargs
    ) -> "HolstebroEngagementUpdate":
        """Create an HolstebroEngagementUpdate from simplified fields."""
        user = PersonRef(uuid=user_uuid)
        job_function = JobFunction(uuid=job_function_uuid)
        return cls(user=user, job_function=job_function, **kwargs)

    async def sync_to_mo(self, context: Context):
        async def get_engagement_uuids(gql_client, employee_uuid):
            query = gql(
                """
            query GetEngagementUuids($employees: [UUID!]) {
              engagements(employees: $employees) {
                objects {
                  current {
                    uuid
                  }
                }
              }
            }
            """
            )
            result = await gql_client.execute(
                query,
                variable_values=jsonable_encoder(
                    {
                        "employees": employee_uuid,
                    }
                ),
            )

            return [res["current"]["uuid"] for res in result["engagements"]["objects"]]

        async def set_job_title(gql_client, engagement_uuids):
            query = gql(
                """
            mutation SetJobtitles($uuid: UUID, $from: DateTime, $job_function: UUID) {
              engagement_update(
                input: {uuid: $uuid,
                        validity: {from: $from},
                        job_function: $job_function}
              ) {
                uuid
              }
            }
            """
            )

            for uuid in engagement_uuids:
                await gql_client.execute(
                    query,
                    variable_values=jsonable_encoder(
                        {
                            "uuid": uuid,
                            "from": datetime.datetime.now().date(),
                            "job_function": self.job_function.uuid,
                        }
                    ),
                )

        engagement_uuids = await get_engagement_uuids(
            gql_client=context["user_context"]["gql_client_v7"],
            employee_uuid=self.user.uuid,
        )
        await set_job_title(
            gql_client=context["user_context"]["gql_client_v7"],
            engagement_uuids=engagement_uuids,
        )

        return engagement_uuids
