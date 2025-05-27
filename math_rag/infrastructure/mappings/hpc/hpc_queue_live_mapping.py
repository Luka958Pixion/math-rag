from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpc import HPCQueueLive

from .hpc_queue_live_entry_mapping import HPCQueueLiveEntryMapping


class HPCQueueLiveMapping(BaseMapping[HPCQueueLive, str]):
    @staticmethod
    def to_source(target: str) -> HPCQueueLive:
        entries = [HPCQueueLiveEntryMapping.to_source(line) for line in target.strip().splitlines()]

        return HPCQueueLive(entries=entries)

    @staticmethod
    def to_target(source: HPCQueueLive) -> str:
        raise NotImplementedError()
