import numpy as np

from datasets import Dataset, DatasetDict


class DatasetSplitterUtil:
    def split(
        dataset: Dataset,
        *,
        train_ratio: float,
        validation_ratio: float,
        test_ratio: float,
        seed: int,
    ) -> DatasetDict:
        total = train_ratio + validation_ratio + test_ratio

        if not np.isclose(total, 1.0):
            raise ValueError(f'Ratios must sum to 1.0, but got {total:.3f}')

        split_test = dataset.train_test_split(test_size=test_ratio, seed=seed)
        train_validation_dataset = split_test['train']
        test_dataset = split_test['test']

        split_validation = train_validation_dataset.train_test_split(
            test_size=(validation_ratio / (train_ratio + test_ratio)), seed=seed
        )
        train_dataset = split_validation['train']
        validation_dataset = split_validation['test']

        return DatasetDict(
            {
                'train': train_dataset,
                'validation': validation_dataset,
                'test': test_dataset,
            }
        )
