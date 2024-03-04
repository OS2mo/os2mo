from typing import Optional

from .base_model import BaseModel


class Version(BaseModel):
    version: "VersionVersion"


class VersionVersion(BaseModel):
    mo_version: Optional[str]
    mo_hash: Optional[str]


Version.update_forward_refs()
VersionVersion.update_forward_refs()
