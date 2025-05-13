import numpy as np

from datasets import Dataset, DatasetDict

from math_rag.application.models.datasets import DatasetSplitSettings


class DatasetSplitterUtil:
    @staticmethod
    def split(dataset: Dataset, settings: DatasetSplitSettings) -> DatasetDict:
        train_ratio, validate_ratio, test_ratio, seed = (
            settings.train_ratio,
            settings.validate_ratio,
            settings.test_ratio,
            settings.seed,
        )
        total = train_ratio + validate_ratio + test_ratio

        if not np.isclose(total, 1.0):
            raise ValueError(f'Ratios must sum to 1.0, but got {total:.3f}')

        split_test = dataset.train_test_split(test_size=test_ratio, seed=seed)
        train_validate_dataset = split_test['train']
        test_dataset = split_test['test']

        split_validate = train_validate_dataset.train_test_split(
            test_size=(validate_ratio / (train_ratio + test_ratio)), seed=seed
        )
        train_dataset = split_validate['train']
        validate_dataset = split_validate['test']

        return DatasetDict(
            {
                'train': train_dataset,
                'validate': validate_dataset,
                'test': test_dataset,
            }
        )
