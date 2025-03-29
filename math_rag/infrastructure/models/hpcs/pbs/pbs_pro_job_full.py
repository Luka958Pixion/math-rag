from datetime import datetime, timedelta
from pathlib import Path

from pydantic import BaseModel

from math_rag.infrastructure.enums.hpcs import HPCQueue
from math_rag.infrastructure.enums.hpcs.pbs import (
    PBSProHoldType,
    PBSProJobState,
    PBSProJoinPath,
    PBSProKeepFiles,
    PBSProMailPoints,
)

from .pbs_pro_resource_list import PBSProResourceList
from .pbs_pro_resources_used import PBSProResourcesUsed
from .pbs_pro_variable_list import PBSProVariableList


class PBSProJobFull(BaseModel):
    id: str
    name: str
    owner: str
    state: PBSProJobState
    queue: HPCQueue
    server: str
    checkpoint: str
    exec_host: str
    exec_vnode: str
    error_path: str
    output_path: str
    dir: Path
    hold_types: PBSProHoldType
    join_path: PBSProJoinPath
    keep_files: PBSProKeepFiles
    mail_points: PBSProMailPoints
    substate: int
    priority: int
    session_id: str
    rerunable: bool
    run_count: int
    submit_arguments: str
    project: str
    submit_host: str
    created: datetime
    queued: datetime
    modified: datetime
    started: datetime
    eligible: datetime
    eligible_delta: timedelta
    resource_list: PBSProResourceList
    resources_used: PBSProResourcesUsed
    variable_list: PBSProVariableList
