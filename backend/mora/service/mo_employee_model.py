from uuid import UUID
from pydantic.main import BaseModel
from pydantic.config import Extra

class Org(BaseModel):
    name: str
    user_key: str
    uuid: UUID

class MOEmployeeWrite(BaseModel):
    name: str
    cpr_no: str
    org: Org
    details: list

    class Config:
        extra = Extra.forbid




