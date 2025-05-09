from pydantic import BaseModel, Field

from math_rag.infrastructure.enums.hpc.prometheus import PrometheusSnapshotStatus

from .prometheus_snapshot_data import PrometheusSnapshotData


class PrometheusSnapshotResponse(BaseModel):
    status: PrometheusSnapshotStatus
    data: PrometheusSnapshotData | None = None
    error_type: str | None = Field(default=None, alias='errorType')
    error: str | None = None

    class Config:
        validate_by_name = True
        populate_by_name = True
