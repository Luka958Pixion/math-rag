from datetime import datetime
from pathlib import Path

from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpcs.pbs import (
    PBSProJob,
    PBSProResourceList,
    PBSProResourcesUsed,
)
from math_rag.infrastructure.utils import HPCParserUtil

from .pbs_pro_variable_list_mapping import PBSProVariableListMapping


DATETIME_FORMAT = '%a %b %d %H:%M:%S %Y'


class PBSProJobMapping(BaseMapping[PBSProJob, str]):
    @staticmethod
    def to_source(target: str) -> PBSProJob:
        fields = HPCParserUtil.parse(target)

        return PBSProJob(
            id=fields['job_id'],
            name=fields['job_name'],
            owner=fields['job_owner'],
            state=fields['job_state'],
            queue=fields['queue'],
            server=fields['server'],
            checkpoint=fields['checkpoint'],
            exec_host=fields['exec_host'],
            exec_vnode=fields['exec_vnode'],
            error_path=fields['error_path'],
            output_path=fields['output_path'],
            dir=Path(fields['jobdir']),
            hold_types=fields['hold_types'],
            join_path=fields['join_path'],
            keep_files=fields['keep_files'],
            mail_points=fields['mail_points'],
            substate=fields['substate'],
            priority=fields['priority'],
            session_id=fields['session_id'],
            rerunable=fields['rerunable'],
            run_count=fields['run_count'],
            submit_arguments=fields['submit_arguments'],
            project=fields['project'],
            submit_host=fields['submit_host'],
            created=datetime.strptime(fields['ctime'], DATETIME_FORMAT),
            queued=datetime.strptime(fields['qtime'], DATETIME_FORMAT),
            modified=datetime.strptime(fields['mtime'], DATETIME_FORMAT),
            started=datetime.strptime(fields['stime'], DATETIME_FORMAT),
            eligible=datetime.strptime(fields['etime'], DATETIME_FORMAT),
            eligible_delta=fields['eligible_time'],
            resource_list=PBSProResourceList(
                mem=HPCParserUtil.parse_memory(fields['resource_list.mem']),
                num_cpus=fields['resource_list.ncpus'],
                num_gpus=fields['resource_list.ngpus'],
                num_nodes=fields['resource_list.nodect'],
                place=fields['resource_list.place'],
                select=fields['resource_list.select'],
                walltime=fields['resource_list.walltime'],
            ),
            resources_used=PBSProResourcesUsed(
                cpu_percent=fields['resources_used.cpupercent'],
                cpu_time=fields['resources_used.cput'],
                num_cpus=fields['resources_used.ncpus'],
                mem=HPCParserUtil.parse_memory(fields['resources_used.mem']),
                vmem=HPCParserUtil.parse_memory(fields['resources_used.vmem']),
                walltime=fields['resources_used.walltime'],
            ),
            variable_list=PBSProVariableListMapping.to_source('variable_list'),
        )

    @staticmethod
    def to_target(source: PBSProJob) -> str:
        raise NotImplementedError()
