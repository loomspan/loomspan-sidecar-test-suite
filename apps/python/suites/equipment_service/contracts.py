"""Application input shapes, equivalent to the Java skill method signatures."""
from pydantic import BaseModel, ConfigDict, StrictBool, StrictInt, StrictStr


class ClosedInput(BaseModel):
    model_config = ConfigDict(extra='forbid')


class LookupInput(ClosedInput):
    caseId: StrictStr
    assetId: StrictStr


class RepairScope(ClosedInput):
    repairHours: StrictInt
    parts: list[StrictStr]
    onlyIfJustifiedByTechnician: StrictBool


class Approval(ClosedInput):
    assessmentVersion: StrictStr
    option: StrictStr
    quoteId: StrictStr
    attendance: StrictStr
    scope: RepairScope
    cap: StrictInt
    idempotencyKey: StrictStr
    approved: StrictBool


class ServiceRequestInput(ClosedInput):
    approval: Approval
