from typing import TypeVar

from pydantic import BaseModel


T = TypeVar('T', bound=BaseModel)


class PydanticOverriderUtil:
    @staticmethod
    def override_non_none_fields(original: T, override: T) -> T:
        original_dict = original.model_dump()
        override_dict = override.model_dump()
        result = {
            k: override_dict[k] if override_dict[k] is not None else original_dict[k]
            for k in original_dict
        }

        return original.__class__(**result)
