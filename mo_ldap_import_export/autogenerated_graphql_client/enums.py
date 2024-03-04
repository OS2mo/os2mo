from enum import Enum


class AuditLogModel(str, Enum):
    AUDIT_LOG = "AUDIT_LOG"
    PERSON = "PERSON"
    FACET = "FACET"
    IT_SYSTEM = "IT_SYSTEM"
    CLASS = "CLASS"
    ORGANISATION = "ORGANISATION"
    ORGANISATION_UNIT = "ORGANISATION_UNIT"
    ORGANISATION_FUNCTION = "ORGANISATION_FUNCTION"


class FileStore(str, Enum):
    EXPORTS = "EXPORTS"
    INSIGHTS = "INSIGHTS"


class OwnerInferencePriority(str, Enum):
    ENGAGEMENT = "ENGAGEMENT"
    ASSOCIATION = "ASSOCIATION"
