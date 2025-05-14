from pydantic import BaseModel


class DatasetMetadataFile(BaseModel):
    name: str
    content: bytes
