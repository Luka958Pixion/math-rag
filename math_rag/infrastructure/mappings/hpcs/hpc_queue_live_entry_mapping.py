from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.enums.hpcs import HPCQueue
from math_rag.infrastructure.models.hpcs import HPCQueueLiveEntry


class HPCQueueLiveEntryMapping(BaseMapping[HPCQueueLiveEntry, str]):
    @staticmethod
    def to_source(target: str) -> HPCQueueLiveEntry:
        fields = target.strip().split()

        queue = HPCQueue(fields[0])
        num_cpus_free, num_cpus_total = map(int, fields[1].split('/'))
        num_gpus_free, num_gpus_total = map(int, fields[2].split('/'))
        num_nodes_free, num_nodes_total = map(int, fields[3].split('/'))
        num_nodes_unavailable, num_nodes_unavailable_total = map(
            int, fields[4].split('/')
        )

        return HPCQueueLiveEntry(
            queue=queue,
            num_cpus_free=num_cpus_free,
            num_cpus_total=num_cpus_total,
            num_gpus_free=num_gpus_free,
            num_gpus_total=num_gpus_total,
            num_nodes_free=num_nodes_free,
            num_nodes_total=num_nodes_total,
            num_nodes_unavailable=num_nodes_unavailable,
            num_nodes_unavailable_total=num_nodes_unavailable_total,
        )

    @staticmethod
    def to_target(source: HPCQueueLiveEntry) -> str:
        raise NotImplementedError()
