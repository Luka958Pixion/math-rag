from datetime import datetime
from pathlib import Path

from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpcs.pbs import PBSProJob
from math_rag.infrastructure.utils import HPCParserUtil

from .pbs_pro_resource_list_mapping import PBSProResourceListMapping
from .pbs_pro_resources_used_mapping import PBSProResourcesUsedMapping
from .pbs_pro_variable_list_mapping import PBSProVariableListMapping


DATETIME_FORMAT = '%a %b %d %H:%M:%S %Y'


class PBSProJobMapping(BaseMapping[PBSProJob, str]):
    @staticmethod
    def to_source(target: str) -> PBSProJob:
        fields = HPCParserUtil.parse(target)
        resource_list_fields = {
            key: value
            for key, value in fields.items()
            if key.startswith('resource_list')
        }
        resources_used_fields = {
            key: value
            for key, value in fields.items()
            if key.startswith('resources_used')
        }

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
            resource_list=PBSProResourceListMapping.to_source(resource_list_fields),
            resources_used=PBSProResourcesUsedMapping.to_source(resources_used_fields),
            variable_list=PBSProVariableListMapping.to_source(fields['variable_list']),
        )

    @staticmethod
    def to_target(source: PBSProJob) -> str:
        raise NotImplementedError()
