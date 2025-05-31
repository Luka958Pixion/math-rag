from abc import ABC
from typing import Any, Self, override

from pydantic import BaseModel


class BaseDocument(ABC, BaseModel):
    @override
    def model_dump(self, **kwargs) -> dict[str, Any]:
        model_dict = super().model_dump(**kwargs)

        if 'id' in model_dict:
            model_dict['_id'] = model_dict.pop('id')

        return model_dict

    @override
    @classmethod
    def model_validate(cls, obj: Any, **kwargs) -> Self:
        if isinstance(obj, dict) and '_id' in obj:
            obj['id'] = obj.pop('_id')

        return super().model_validate(obj, **kwargs)
