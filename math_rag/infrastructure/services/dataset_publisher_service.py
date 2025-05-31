from logging import getLogger

from huggingface_hub import HfApi
from huggingface_hub.errors import RepositoryNotFoundError

from math_rag.application.base.services import BaseDatasetPublisherService
from math_rag.application.models.datasets import (
    DatasetMetadataFile,
    DatasetSplitSettings,
)
from math_rag.core.base import BaseDataset
from math_rag.infrastructure.mappings.datasets import DatasetMapping
from math_rag.infrastructure.utils import DatasetSplitterUtil


logger = getLogger(__name__)


class DatasetPublisherService(BaseDatasetPublisherService):
    def __init__(
        self,
        hugging_face_base_url: str,
        hugging_face_username: str,
        hugging_face_token: str,
    ):
        self.hugging_face_base_url = hugging_face_base_url
        self.hugging_face_username = hugging_face_username
        self.hugging_face_token = hugging_face_token
        self.hugging_face_api = HfApi()

    def publish(
        self,
        dataset: BaseDataset,
        dataset_split_settings: DatasetSplitSettings,
        dataset_metadata_file: DatasetMetadataFile | None = None,
    ):
        repo_id = f'{self.hugging_face_username}/{dataset.__class__.__name__.lower()}'

        # create a repository if it doesn't exist
        try:
            self.hugging_face_api.dataset_info(repo_id, token=self.hugging_face_token)
            logger.info(f'Dataset {repo_id} already exists')

        except RepositoryNotFoundError:
            repo_url = self.hugging_face_api.create_repo(
                repo_id, repo_type='dataset', token=self.hugging_face_token
            )
            logger.info(f'Dataset {repo_id} created, view it at: {repo_url.url}')

        # push a metadata file
        self.hugging_face_api.upload_file(
            path_or_fileobj=dataset_metadata_file.content,
            path_in_repo=dataset_metadata_file.name,
            repo_id=repo_id,
            token=self.hugging_face_token,
            repo_type='dataset',
        )

        # map dataset to huggingface
        hf_dataset = DatasetMapping.to_target(dataset)

        # split
        dataset_dict = DatasetSplitterUtil.split(hf_dataset, dataset_split_settings)

        # push the datasets
        dataset_dict.push_to_hub(
            repo_id,
            config_name=str(dataset.id),
            private=True,
            token=self.hugging_face_token,
        )
