from pathlib import Path

from pydantic import BaseModel, Field

from .pbs_pro_resource_list import PBSProResourceList
from .pbs_pro_resources_used import PBSProResourcesUsed
from .pbs_pro_time import PBSProTime
from .pbs_pro_variable_list import PBSProVariableList


class PBSProJob(BaseModel):
    id: str = Field(alias='job_id')
    name: str = Field(alias='job_name')
    owner: str = Field(alias='job_owner')
    state: str = Field(alias='job_state')
    queue: str = Field(alias='queue')
    server: str = Field(alias='server')
    checkpoint: str = Field(alias='checkpoint')
    exec_host: str = Field(alias='exec_host')
    exec_vnode: str = Field(alias='exec_vnode')
    error_path: str = Field(alias='error_path')
    output_path: str = Field(alias='output_path')
    dir: Path = Field(alias='jobdir')
    hold_types: str = Field(alias='hold_types')
    join_path: str = Field(alias='join_path')
    keep_files: str = Field(alias='keep_files')
    mail_points: str = Field(alias='mail_points')
    substate: int = Field(alias='substate')
    priority: int = Field(alias='priority')
    session_id: str = Field(alias='session_id')
    rerunable: bool = Field(alias='rerunable')
    run_count: int = Field(alias='run_count')
    submit_arguments: str = Field(alias='submit_arguments')
    project: str = Field(alias='project')
    submit_host: str = Field(alias='submit_host')

    # TODO
    resource_list: PBSProResourceList
    resources_used: PBSProResourcesUsed
    time: PBSProTime
    variable_list: PBSProVariableList
