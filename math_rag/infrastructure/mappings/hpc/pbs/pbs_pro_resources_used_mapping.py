from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpc.pbs import PBSProResourcesUsed
from math_rag.infrastructure.utils import FormatParserUtil


class PBSProResourcesUsedMapping(BaseMapping[PBSProResourcesUsed, str]):
    @staticmethod
    def to_source(target: dict[str, str]) -> PBSProResourcesUsed:
        return PBSProResourcesUsed(
            cpu_percent=target['resources_used.cpupercent'],
            cpu_time=FormatParserUtil.parse_timedelta(target['resources_used.cput']),
            num_cpus=target['resources_used.ncpus'],
            mem=FormatParserUtil.parse_memory(target['resources_used.mem']),
            vmem=FormatParserUtil.parse_memory(target['resources_used.vmem']),
            walltime=FormatParserUtil.parse_timedelta(
                target['resources_used.walltime']
            ),
        )

    @staticmethod
    def to_target(source: PBSProResourcesUsed) -> str:
        raise NotImplementedError()
