from uuid import UUID

from mora import mapping
from mora.graphapi.models import EmployeeCreate
from mora.graphapi.types import EmployeeType
from mora.service.employee import EmployeeRequestHandler


async def create(ec: EmployeeCreate) -> EmployeeType:
    request = await EmployeeRequestHandler.construct(
        ec.dict(), mapping.RequestType.CREATE
    )
    uuid = await request.submit()

    return EmployeeType(uuid=UUID(uuid))
