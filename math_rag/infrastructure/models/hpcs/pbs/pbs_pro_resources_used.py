from datetime import timedelta

from pydantic import BaseModel, Field, field_validator

from math_rag.infrastructure.utils import PBSProParserUtil


class PBSProResourcesUsed(BaseModel):
    cpu_percent: int = Field(alias='resources_used.cpupercent')
    cpu_time: timedelta = Field(alias='resources_used.cput')
    num_cpus: int = Field(alias='resources_used.ncpus')
    memory: int = Field(alias='resources_used.mem')
    virtual_memory: int = Field(alias='resources_used.vmem')
    walltime: timedelta = Field(alias='resources_used.walltime')

    @field_validator('memory', 'virtual_memory', mode='before')
    def parse_memory(cls, value: str):
        return PBSProParserUtil.parse_memory(value)
