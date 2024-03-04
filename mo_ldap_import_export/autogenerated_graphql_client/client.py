from .async_base_client import AsyncBaseClient
from .create_it_system import CreateItSystem
from .create_it_system import CreateItSystemItsystemCreate
from .input_types import ITSystemCreateInput


def gql(q: str) -> str:
    return q


class GraphQLClient(AsyncBaseClient):
    async def create_it_system(
        self, input: ITSystemCreateInput
    ) -> CreateItSystemItsystemCreate:
        query = gql(
            """
            mutation create_it_system($input: ITSystemCreateInput!) {
              itsystem_create(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateItSystem.parse_obj(data).itsystem_create
