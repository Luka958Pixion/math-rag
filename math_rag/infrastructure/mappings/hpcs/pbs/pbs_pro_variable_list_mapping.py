from pathlib import Path

from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.hpcs.pbs import PBSProVariableList


class PBSProVariableListMapping(BaseMapping[PBSProVariableList, str]):
    @staticmethod
    def to_source(target: str) -> PBSProVariableList:
        fields: dict[str, str] = {}

        for pair in target.split(','):
            if pair.startswith('PBS_') and '=' in pair:
                key, value = pair.split('=', 1)
                fields[key] = value

        return PBSProVariableList(
            home=Path(fields['PBS_O_HOME']) if 'PBS_O_HOME' in fields else None,
            paths=[Path(path) for path in fields['PBS_O_PATH'].split(':') if path]
            if 'PBS_O_PATH' in fields
            else [],
            mail=fields.get('PBS_O_MAIL'),
            shell=fields.get('PBS_O_SHELL'),
            workdir=Path(fields['PBS_O_WORKDIR'])
            if 'PBS_O_WORKDIR' in fields
            else None,
            host=fields.get('PBS_O_HOST'),
            lang=fields.get('PBS_O_LANG'),
            logname=fields.get('PBS_O_LOGNAME'),
            system=fields.get('PBS_O_SYSTEM'),
            queue=fields.get('PBS_O_QUEUE'),
            tz=fields.get('PBS_O_TZ'),
            environment=fields.get('PBS_ENVIRONMENT'),
            jobdir=Path(fields['PBS_JOBDIR']) if 'PBS_JOBDIR' in fields else None,
            jobid=fields.get('PBS_JOBID'),
            jobname=fields.get('PBS_JOBNAME'),
            nodefile=Path(fields['PBS_NODEFILE']) if 'PBS_NODEFILE' in fields else None,
            execution_queue=fields.get('PBS_QUEUE'),
            tmpdir=Path(fields['PBS_TMPDIR']) if 'PBS_TMPDIR' in fields else None,
        )

    @staticmethod
    def to_target(source: PBSProVariableList) -> str:
        raise NotImplementedError()
