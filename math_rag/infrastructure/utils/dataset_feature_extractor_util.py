from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from datasets import ClassLabel, Features, Value
from pydantic import BaseModel

from math_rag.shared.utils import TypeUtil


TYPE_DICT: dict[type[Any], str] = {
    str: 'string',
    int: 'int64',
    float: 'float64',
    bool: 'bool',
    UUID: 'string',
    datetime: 'timestamp[ms]',
}


class DatasetFeatureExtractorUtil:
    @staticmethod
    def extract(model_type: type[BaseModel], fields: list[str]) -> Features:
        """
        Convert a Pydantic BaseModel into a Hugging Face Datasets Features mapping.
        """
        for field in fields:
            if field not in model_type.model_fields:
                raise ValueError(f'Field {field} does not exist in model {model_type.__name__}')

        features: dict[str, Value] = {}

        for name, field_info in model_type.model_fields.items():
            if name not in fields:
                continue

            annotation = TypeUtil.extract_optional_type(field_info.annotation)

            if isinstance(annotation, type) and issubclass(annotation, Enum):
                class_label_names = [member.value for member in annotation]
                features[name] = ClassLabel(names=class_label_names)
                continue

            if annotation in TYPE_DICT:
                features[name] = Value(TYPE_DICT[annotation])
                continue

            raise TypeError(
                f'Unsupported type for field {name}: {annotation}, '
                f'allowed: {list(TYPE_DICT)} or Enum or Optional[...] of them'
            )

        return Features(features)
