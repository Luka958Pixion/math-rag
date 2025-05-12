from datetime import datetime

from datasets import DatasetInfo

from math_rag.application.base.datasets import BaseDataset, BaseSample
from math_rag.infrastructure.mappings.datasets import DatasetMapping
from math_rag.infrastructure.utils import (
    DatasetFeatureExtractorUtil,
    DatasetSplitterUtil,
)


class DatasetPublisherService:
    def __init__(
        self,
        hugging_face_token: str,
        hugging_face_repository_id: str,
        hugging_face_datasets_url: str,
    ):
        self.hugging_face_token = hugging_face_token
        self.hugging_face_repository_id = hugging_face_repository_id
        self.hugging_face_datasets_url = hugging_face_datasets_url

    def publish(self, dataset: BaseDataset, sample_type: type[BaseSample]):
        citation_key = dataset.__class__.__name__.lower()
        author = 'Luka Panić'
        title = dataset.__class__.__name__
        year = datetime.now().year
        url = self.hugging_face_datasets_url

        citation = '\n'.join(
            [
                f'@misc{{{citation_key},',
                f'  author = {{{author}}},',
                f'  title = {{{title}}},',
                f'  year = {{{year}}},',
                f'  url = {{{url}}}',
                '}',
            ]
        )

        sample_fields = list(BaseSample.model_fields.keys())
        sample_features = DatasetFeatureExtractorUtil.extract(sample_type)

        info = DatasetInfo(
            description=f'A dataset with: {",".join(sample_fields)}',
            version='1.0.0',
            features=sample_features,
            license='mit',
            citation=citation,
        )

        hf_dataset = DatasetMapping.to_target(dataset).shuffle(seed=42)
        dataset_dict = DatasetSplitterUtil.split(
            hf_dataset, train_ratio=0.8, validation_ratio=0.1, test_ratio=0.1, seed=42
        )
        dataset_dict.info = info
        dataset_dict.push_to_hub(
            self.hugging_face_repository_id,
            private=True,
            token=self.hugging_face_token,
        )
