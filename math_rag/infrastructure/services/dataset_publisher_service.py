from enum import Enum
from logging import getLogger
from uuid import UUID

from datasets import Dataset, DatasetInfo
from huggingface_hub import HfApi
from huggingface_hub.errors import RepositoryNotFoundError

from math_rag.application.base.services import BaseDatasetPublisherService
from math_rag.application.models.datasets import DatasetMetadataFile
from math_rag.core.models import DatasetSplit
from math_rag.core.types import SampleType
from math_rag.infrastructure.utils import DatasetFeatureExtractorUtil, DatasetSplitterUtil


logger = getLogger(__name__)


class DatasetPublisherService(BaseDatasetPublisherService):
    def __init__(
        self,
        hugging_face_api: HfApi,
        hugging_face_username: str,
        hugging_face_token: str,
    ):
        self.hugging_face_api = hugging_face_api
        self.hugging_face_username = hugging_face_username
        self.hugging_face_token = hugging_face_token

    def publish(
        self,
        dataset_id: UUID,
        dataset_name: str,
        samples: list[SampleType],
        sample_type: type[SampleType],
        fields: list[str],
        dataset_splits: list[DatasetSplit],
        dataset_metadata_file: DatasetMetadataFile | None = None,
    ):
        # create a repository if it doesn't exist
        repo_id = f'{self.hugging_face_username}/{dataset_name}'

        try:
            self.hugging_face_api.dataset_info(repo_id)
            logger.info(f'Dataset {repo_id} already exists')

        except RepositoryNotFoundError:
            repo_url = self.hugging_face_api.create_repo(repo_id, private=True, repo_type='dataset')
            logger.info(f'Dataset {repo_id} created, view it at: {repo_url.url}')

        # upload metadata file
        self.hugging_face_api.upload_file(
            path_or_fileobj=dataset_metadata_file.content,
            path_in_repo=dataset_metadata_file.name,
            repo_id=repo_id,
            repo_type='dataset',
        )

        # map to huggingface
        mapping = [
            {
                name: (value.value if isinstance(value, Enum) else value)
                for name, value in sample.model_dump(mode='python', include=fields).items()
            }
            for sample in samples
        ]
        features = DatasetFeatureExtractorUtil.extract(sample_type, fields)
        info = DatasetInfo(license='mit', features=features)
        dataset = Dataset.from_list(
            mapping=mapping,
            features=features,
            info=info,
            split=None,
        )
        dataset = dataset.shuffle(seed=42)

        # split
        dataset_dict = DatasetSplitterUtil.split(dataset, dataset_splits)

        # push the datasets
        dataset_dict.push_to_hub(
            repo_id, config_name=str(dataset_id), private=True, token=self.hugging_face_token
        )

    def unpublish(self, dataset_name: str):
        repo_id = f'{self.hugging_face_username}/{dataset_name}'

        try:
            self.hugging_face_api.dataset_info(repo_id)

        except RepositoryNotFoundError:
            logger.warning(f'Dataset {repo_id} does not exist, nothing to unpublish')

            return

        self.hugging_face_api.delete_repo(repo_id=repo_id, repo_type='dataset')
        logger.info(f'Dataset {repo_id} deleted')
