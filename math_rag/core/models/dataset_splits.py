import numpy as np

from pydantic import RootModel, model_validator

from .dataset_split import DatasetSplit


class DatasetSplits(RootModel[list[DatasetSplit]]):
    @model_validator(mode='after')
    def check_ratios_sum_to_one(self) -> 'DatasetSplits':
        total = sum(split.ratio for split in self.root)

        if not np.isclose(total, 1.0):
            raise ValueError(f'Ratios must sum to 1.0, got {total}')

        return self
