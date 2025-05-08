from pydantic import BaseModel


class PrometheusSnapshotData(BaseModel):
    name: str
