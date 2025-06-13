from datasets import Dataset, DatasetDict

from math_rag.core.models import DatasetSplits


class DatasetSplitterUtil:
    @staticmethod
    def split(dataset: Dataset, splits: DatasetSplits) -> DatasetDict:
        n = len(dataset)

        # extract ratios and compute base counts
        counts = [int(s.ratio * n) for s in splits.root]

        # adjust last count to pick up any rounding remainder
        counts[-1] = n - sum(counts[:-1])

        # slice the dataset into named splits
        result = {}
        start = 0

        for split, count in zip(splits.root, counts):
            end = start + count
            result[split.name] = dataset.select(range(start, end))
            start = end

        return DatasetDict(result)
