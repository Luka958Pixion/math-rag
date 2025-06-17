from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel

from .annotation import Annotation
from .prediction import Prediction


T = TypeVar('T', bound=BaseModel)


class Task(BaseModel, Generic[T]):
    id: int
    data: T
    annotations: list[Annotation]
    drafts: list[Annotation]
    predictions: list[Prediction]
    meta: dict[str, str]
    created_at: datetime
    updated_at: datetime
    inner_id: int
    total_annotations: int
    cancelled_annotations: int
    total_predictions: int
    comment_count: int
    unresolved_comment_count: int
    last_comment_updated_at: datetime | None
    project: int
    updated_by: int
    comment_authors: list[int]
