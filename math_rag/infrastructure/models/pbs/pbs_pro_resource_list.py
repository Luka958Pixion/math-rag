from datetime import timedelta

from pydantic import BaseModel, Field, field_validator

from math_rag.infrastructure.models.validators import PBSProValidator


class PBSProResourceList(BaseModel):
    memory: int = Field(alias='resource_list.mem')
    num_cpus: int = Field(alias='resource_list.ncpus')
    num_gpus: int = Field(alias='resource_list.ngpus')
    num_nodes: int = Field(alias='resource_list.nodect')
    place: str = Field(alias='resource_list.place')
    select: str = Field(alias='resource_list.select')
    walltime: timedelta = Field(alias='resource_list.walltime')

    @field_validator('memory', mode='before')
    def parse_memory(cls, value: str):
        return PBSProValidator.parse_memory(value)
