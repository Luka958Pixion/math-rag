from enum import Enum
from typing import TypeVar

from label_studio_sdk.label_interface import LabelInterface
from label_studio_sdk.label_interface.create import choices


LabelType = TypeVar('LabelType', bound=Enum)


class LabelInterfaceBuilderUtil:
    def build(
        self,
        label_type: type[LabelType],
    ) -> int:
        labels = [label.value for label in label_type]
        tags = {
            'html': 'HyperText',
            'latex': 'Text',
            'label': choices(labels),
        }

        return LabelInterface.create(tags)
