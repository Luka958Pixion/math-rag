from math_rag.core.enums import TaskStatus
from math_rag.core.models import Task
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import TaskDocument


class TaskMapping(BaseMapping[Task, TaskDocument]):
    @staticmethod
    def to_source(target: TaskDocument) -> Task:
        return Task(
            id=target.id,
            model_id=target.model_id,
            model_type=target.model_type,
            created_at=target.created_at,
            started_at=target.started_at,
            failed_at=target.failed_at,
            finished_at=target.finished_at,
            task_status=TaskStatus(target.task_status),
        )

    @staticmethod
    def to_target(source: Task) -> TaskDocument:
        return TaskDocument(
            id=source.id,
            model_id=source.model_id,
            model_type=source.model_type,
            created_at=source.created_at,
            started_at=source.started_at,
            failed_at=source.failed_at,
            finished_at=source.finished_at,
            task_status=source.task_status.value,
        )
