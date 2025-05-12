from datetime import datetime

from datasets import DatasetInfo
from huggingface_hub import HfApi, create_repo
from requests.exceptions import HTTPError

from math_rag.application.base.datasets import BaseDataset, BaseSample
from math_rag.application.models.datasets import DatasetSplitSettings
from math_rag.infrastructure.mappings.datasets import DatasetMapping
from math_rag.infrastructure.utils import (
    DatasetFeatureExtractorUtil,
    DatasetSplitterUtil,
)


class DatasetPublisherService:
    def __init__(
        self,
        hugging_face_token: str,
        hugging_face_datasets_url: str,
    ):
        self.hugging_face_token = hugging_face_token
        self.hugging_face_datasets_url = hugging_face_datasets_url
        self.hugging_face_api = HfApi()

    def publish(
        self,
        dataset: BaseDataset,
        sample_type: type[BaseSample],
        settings: DatasetSplitSettings,
    ):
        repo_id = dataset.__class__.__name__.lower()

        # create a repository if it doesn't exist
        try:
            self.hugging_face_api.dataset_info(repo_id, token=self.hugging_face_token)

        except HTTPError as e:
            if e.response and e.response.status_code == 404:
                create_repo(repo_id, repo_type='dataset', token=self.hugging_face_token)

            else:
                raise

        # create dataset metadata
        citation_key = repo_id
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

        # map dataset to huggingface
        hf_dataset = DatasetMapping.to_target(dataset).shuffle(seed=42)
        dataset_dict = DatasetSplitterUtil.split(hf_dataset, settings)
        dataset_dict.info = info
        dataset_dict.push_to_hub(
            repo_id,
            private=True,
            token=self.hugging_face_token,
        )
