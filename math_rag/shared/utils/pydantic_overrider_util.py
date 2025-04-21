from typing import TypeVar

from pydantic import BaseModel


T = TypeVar('T', bound=BaseModel)


class PydanticOverriderUtil:
    @staticmethod
    def override(original: T, override: T) -> T:
        # overrides properties that are explicilty set in the override variable
        original_dict = original.model_dump()
        override_dict = override.model_dump()

        result = {
            key: override_dict[key]
            if key in override.model_fields_set
            else original_dict[key]
            for key in original_dict
        }

        return original.__class__(**result)
