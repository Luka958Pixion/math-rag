from datetime import timedelta

from pydantic import BaseModel, Field, field_validator

from math_rag.infrastructure.utils import HPCParserUtil


class PBSProResourcesUsed(BaseModel):
    cpu_percent: int = Field(alias='resources_used.cpupercent')
    cpu_time: timedelta = Field(alias='resources_used.cput')
    num_cpus: int = Field(alias='resources_used.ncpus')
    mem: int = Field(alias='resources_used.mem')
    vmem: int = Field(alias='resources_used.vmem')
    walltime: timedelta = Field(alias='resources_used.walltime')

    @field_validator('mem', 'vmem', mode='before')
    def parse_memory(cls, value: str):
        return HPCParserUtil.parse_memory(value)
