from uuid import UUID

from .base_model import BaseModel


class LeaveRefresh(BaseModel):
    leave_refresh: "LeaveRefreshLeaveRefresh"


class LeaveRefreshLeaveRefresh(BaseModel):
    objects: list[UUID]


LeaveRefresh.update_forward_refs()
LeaveRefreshLeaveRefresh.update_forward_refs()
