from logging import getLogger
from pathlib import Path
from uuid import UUID

from datasets import load_dataset
from datasets.download import DownloadConfig
from huggingface_hub import HfApi, hf_hub_download
from huggingface_hub.errors import RepositoryNotFoundError

from math_rag.application.base.services import BaseDatasetLoaderService
from math_rag.application.models.datasets import DatasetMetadataFile
from math_rag.core.types import SampleType


logger = getLogger(__name__)


class DatasetLoaderService(BaseDatasetLoaderService):
    def __init__(
        self,
        hugging_face_api: HfApi,
        hugging_face_username: str,
        hugging_face_token: str,
    ):
        self.hugging_face_api = hugging_face_api
        self.hugging_face_username = hugging_face_username
        self.hugging_face_token = hugging_face_token

    def load(
        self,
        dataset_id: UUID,
        dataset_name: str,
        dataset_metadata_file_name: str | None,
        sample_type: type[SampleType],
        *,
        max_retries: int,
    ) -> tuple[dict[str, list[SampleType]], DatasetMetadataFile | None]:
        # check if repository exists
        repo_id = f'{self.hugging_face_username}/{dataset_name}'

        try:
            self.hugging_face_api.dataset_info(repo_id, token=self.hugging_face_token)

        except RepositoryNotFoundError:
            raise ValueError(f'Dataset {repo_id} does not exist')

        # load dataset
        download_config = DownloadConfig(
            max_retries=max_retries,
            disable_tqdm=True,
        )
        dataset_dict = load_dataset(
            path=repo_id,
            name=dataset_id,
            split=None,
            download_config=download_config,
            token=self.hugging_face_token,
            trust_remote_code=True,
        )

        # download metadata file
        dataset_metadata_file = None

        if dataset_metadata_file_name:
            dataset_metadata_file_path = hf_hub_download(
                repo_id=repo_id,
                filename=dataset_metadata_file_name,
                repo_type='dataset',
                token=self.hugging_face_token,
            )
            dataset_metadata_file_content = Path(dataset_metadata_file_path).read_bytes()
            dataset_metadata_file = DatasetMetadataFile(
                name=dataset_metadata_file_name, content=dataset_metadata_file_content
            )

        # map from huggingface
        split_name_to_samples = {}

        # TODO datetime can fail
        for split_name in dataset_dict:
            dataset = dataset_dict[split_name]
            samples = [sample_type.model_validate(row) for row in dataset]
            split_name_to_samples[split_name] = samples

        return split_name_to_samples, dataset_metadata_file
