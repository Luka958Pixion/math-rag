from math_rag.application.base.repositories.documents import BaseTaskRepository

from .partials import PartialTaskTrackerBackgroundService


class IndexBuildTrackerBackgroundService(PartialTaskTrackerBackgroundService):
    def __init__(self, task_repository: BaseTaskRepository):
        self._task_repository = task_repository
