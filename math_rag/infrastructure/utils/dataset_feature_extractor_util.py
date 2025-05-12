from typing import Any
from uuid import UUID

from datasets import Features, Value
from pydantic import BaseModel

from math_rag.shared.utils import TypeUtil


class DatasetFeatureExtractorUtil:
    @staticmethod
    def extract(model: type[BaseModel]) -> Features:
        """
        Convert a Pydantic BaseModel (only primitives and UUID, or their Optional[...])
        into a Hugging Face Datasets Features mapping.
        """
        TYPE_MAP: dict[type[Any], str] = {
            str: 'string',
            int: 'int64',
            float: 'float64',
            bool: 'bool',
            UUID: 'string',
        }

        features: dict[str, Value] = {}

        for name, field in model.model_fields.items():
            annotation = TypeUtil.extract_optional_type(field.annotation)

            if annotation not in TYPE_MAP:
                raise TypeError(
                    f'Unsupported type for field {name}: {annotation}, '
                    f'allowed: {list(TYPE_MAP)} or Optional[...] of them'
                )

            features[name] = Value(TYPE_MAP[annotation])

        return Features(features)
