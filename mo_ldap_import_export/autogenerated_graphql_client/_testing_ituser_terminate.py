from uuid import UUID

from .base_model import BaseModel


class TestingItuserTerminate(BaseModel):
    ituser_terminate: "TestingItuserTerminateItuserTerminate"


class TestingItuserTerminateItuserTerminate(BaseModel):
    uuid: UUID


TestingItuserTerminate.update_forward_refs()
TestingItuserTerminateItuserTerminate.update_forward_refs()
