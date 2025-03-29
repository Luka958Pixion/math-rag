from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpcs.pbs import PBSProResourceList
from math_rag.infrastructure.utils import HPCParserUtil


class PBSProResourceListMapping(BaseMapping[PBSProResourceList, str]):
    @staticmethod
    def to_source(target: dict[str, str]) -> PBSProResourceList:
        return PBSProResourceList(
            mem=HPCParserUtil.parse_memory(target['resource_list.mem']),
            num_cpus=target['resource_list.ncpus'],
            num_gpus=target['resource_list.ngpus'],
            num_nodes=target['resource_list.nodect'],
            place=target['resource_list.place'],
            select=target['resource_list.select'],
            walltime=target['resource_list.walltime'],
        )

    @staticmethod
    def to_target(source: PBSProResourceList) -> str:
        raise NotImplementedError()
