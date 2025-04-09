from dataclasses import is_dataclass
from typing import TypeVar, get_type_hints


T = TypeVar('T')


class DataclassUtil:
    @staticmethod
    def from_dict(cls: type[T], data: dict[str, object]) -> T:
        if not is_dataclass(cls):
            raise ValueError()

        kwargs = {}
        hints = get_type_hints(cls)

        for field, field_type in hints.items():
            value = data.get(field)

            if value is None:
                kwargs[field] = value

            elif isinstance(value, dict) and is_dataclass(field_type):
                kwargs[field] = DataclassUtil.from_dict(field_type, value)

            elif (
                isinstance(value, list)
                and hasattr(field_type, '__origin__')
                and field_type.__origin__ is list
            ):
                inner_type = field_type.__args__[0]
                kwargs[field] = [
                    DataclassUtil.from_dict(inner_type, item)
                    if isinstance(item, dict) and is_dataclass(inner_type)
                    else item
                    for item in value
                ]

            else:
                kwargs[field] = value

        return cls(**kwargs)
