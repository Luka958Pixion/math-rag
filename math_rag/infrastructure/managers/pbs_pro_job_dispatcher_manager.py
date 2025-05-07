from threading import Lock
from uuid import UUID

from .entries import PBSProJobDispatcherEntry


class PBSProJobDispatcherManager:
    def __init__(self):
        self._lock = Lock()
        self._job_id_to_entry: dict[UUID, PBSProJobDispatcherEntry] = {}

    def add_job_id(self, job_id: UUID, listener_classes: set[str]):
        with self._lock:
            entry = self._job_id_to_entry.get(job_id)

            if not entry:
                entry = PBSProJobDispatcherEntry(
                    job_id=job_id, listener_classes=listener_classes
                )
                self._job_id_to_entry[job_id] = entry

            else:
                entry.listener_classes.update(listener_classes)

    def get_job_ids(self, listener_class: str) -> list[UUID]:
        with self._lock:
            job_ids: list[UUID] = []
            job_ids_to_remove: list[UUID] = []

            for job_id, entry in self._job_id_to_entry.items():
                if listener_class in entry.listener_classes:
                    job_ids.append(job_id)
                    entry.listener_classes.remove(listener_class)

                    if not entry.listener_classes:
                        job_ids_to_remove.append(job_id)

            for job_id in job_ids_to_remove:
                del self._job_id_to_entry[job_id]

            return job_ids
