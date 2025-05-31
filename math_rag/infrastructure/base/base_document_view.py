from abc import ABC

from pydantic import BaseModel


class BaseDocumentView(ABC, BaseModel):
    pass
