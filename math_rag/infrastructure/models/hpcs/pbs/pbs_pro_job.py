from datetime import datetime, timedelta
from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from math_rag.infrastructure.enums.hpcs import HPCQueue
from math_rag.infrastructure.enums.hpcs.pbs import (
    PBSProHoldType,
    PBSProJobState,
    PBSProJoinPath,
    PBSProKeepFiles,
    PBSProMailPoints,
)
from math_rag.infrastructure.utils import HPCParserUtil

from .pbs_pro_resource_list import PBSProResourceList
from .pbs_pro_resources_used import PBSProResourcesUsed
from .pbs_pro_time import PBSProTime
from .pbs_pro_variable_list import PBSProVariableList


FORMAT = '%a %b %d %H:%M:%S %Y'


class PBSProJob(BaseModel):
    id: str = Field(alias='job_id')
    name: str = Field(alias='job_name')
    owner: str = Field(alias='job_owner')
    state: PBSProJobState = Field(alias='job_state')
    queue: HPCQueue = Field(alias='queue')
    server: str = Field(alias='server')
    checkpoint: str = Field(alias='checkpoint')
    exec_host: str = Field(alias='exec_host')
    exec_vnode: str = Field(alias='exec_vnode')
    error_path: str = Field(alias='error_path')
    output_path: str = Field(alias='output_path')
    dir: Path = Field(alias='jobdir')
    hold_types: PBSProHoldType = Field(alias='hold_types')
    join_path: PBSProJoinPath = Field(alias='join_path')
    keep_files: PBSProKeepFiles = Field(alias='keep_files')
    mail_points: PBSProMailPoints = Field(alias='mail_points')
    substate: int = Field(alias='substate')
    priority: int = Field(alias='priority')
    session_id: str = Field(alias='session_id')
    rerunable: bool = Field(alias='rerunable')
    run_count: int = Field(alias='run_count')
    submit_arguments: str = Field(alias='submit_arguments')
    project: str = Field(alias='project')
    submit_host: str = Field(alias='submit_host')

    created: datetime = Field(alias='ctime')
    queued: datetime = Field(alias='qtime')
    modified: datetime = Field(alias='mtime')
    started: datetime = Field(alias='stime')
    eligible: datetime = Field(alias='etime')
    eligible_delta: timedelta = Field(alias='eligible_time')

    resource_list: PBSProResourceList
    resources_used: PBSProResourcesUsed
    variable_list: PBSProVariableList

    @field_validator(
        'created', 'queued', 'modified', 'started', 'eligible', mode='before'
    )
    def parse_datetime(cls, value: str) -> datetime:
        return datetime.strptime(value, FORMAT)

    @classmethod
    def from_queue_status(cls, queue_status: str) -> 'PBSProJob':
        queue_status_flat_dict = HPCParserUtil.parse(queue_status)
        time_fields = {field.alias for field in PBSProTime.model_fields.values()}
        variable_list = queue_status_flat_dict.pop('variable_list')

        return cls(
            **queue_status_flat_dict,
            resource_list={
                key: value
                for key, value in queue_status_flat_dict.items()
                if key.startswith('resource_list.')
            },
            resources_used={
                key: value
                for key, value in queue_status_flat_dict.items()
                if key.startswith('resources_used.')
            },
            time={
                key: value
                for key, value in queue_status_flat_dict.items()
                if key in time_fields
            },
            variable_list=HPCParserUtil.parse_variable_list(variable_list),
        )
