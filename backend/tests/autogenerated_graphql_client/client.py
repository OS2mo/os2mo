from .base_client import BaseClient
from .create_organisation import CreateOrganisation
from .create_organisation import CreateOrganisationOrgCreate
from .input_types import OrganisationCreate


def gql(q: str) -> str:
    return q


class GraphQLClient(BaseClient):
    def create_organisation(
        self, input: OrganisationCreate
    ) -> CreateOrganisationOrgCreate:
        query = gql(
            """
            mutation CreateOrganisation($input: OrganisationCreate!) {
              org_create(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateOrganisation.parse_obj(data).org_create
