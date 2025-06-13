import numpy as np

from datasets import Dataset, DatasetDict

from math_rag.core.models import DatasetSplit


class DatasetSplitterUtil:
    @staticmethod
    def split(dataset: Dataset, splits: list[DatasetSplit]) -> DatasetDict:
        # validate
        total = sum(split.ratio for split in splits)

        if not np.isclose(total, 1.0):
            raise ValueError(f'Ratios must sum to 1.0, got {total}')

        n = len(dataset)

        # extract ratios and compute base counts
        counts = [int(split.ratio * n) for split in splits]

        # adjust last count to pick up any rounding remainder
        counts[-1] = n - sum(counts[:-1])

        # slice the dataset into named splits
        result = {}
        start = 0

        for split, count in zip(splits, counts):
            end = start + count
            result[split.name] = dataset.select(range(start, end))
            start = end

        return DatasetDict(result)
