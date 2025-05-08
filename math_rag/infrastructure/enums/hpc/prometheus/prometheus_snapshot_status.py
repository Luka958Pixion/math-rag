from enum import Enum


class PrometheusSnapshotStatus(str, Enum):
    SUCCESS = 'success'
    ERROR = 'error'
