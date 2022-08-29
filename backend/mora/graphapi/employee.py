from mora.graphapi.models import EmployeeCreate
from mora.graphapi.types import EmployeeType


async def create(ec: EmployeeCreate) -> EmployeeType:
    return EmployeeType()
