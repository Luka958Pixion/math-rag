import json

from logging import getLogger
from pathlib import Path
from uuid import UUID

from huggingface_hub.inference._generated.types import ChatCompletionOutput

from math_rag.application.models.inference import (
    LLMBatchRequest,
    LLMBatchResult,
    LLMFailedRequest,
    LLMRequest,
    LLMResponseList,
)
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.clients import PBSProClient, SFTPClient
from math_rag.infrastructure.enums.hpc.pbs import PBSProJobState
from math_rag.infrastructure.inference.partials import PartialBatchLLM
from math_rag.infrastructure.mappings.inference.huggingface import (
    LLMErrorMapping,
    LLMRequestMapping,
    LLMResponseListMapping,
)
from math_rag.infrastructure.utils import BytesStreamerUtil, FileStreamerUtil


logger = getLogger(__name__)


class HuggingFaceBatchLLM(PartialBatchLLM):
    def __init__(
        self,
        root_path: Path,
        pbs_pro_client: PBSProClient,
        sftp_client: SFTPClient,
        apptainer_service,
    ):
        self.root_path = root_path
        self.pbs_pro_client = pbs_pro_client
        self.sftp_client = sftp_client

        from math_rag.infrastructure.clients import ApptainerClient
        from math_rag.infrastructure.services import ApptainerService

        apptainer_client = ApptainerClient()

        def_file_path = Path(...)  # TODO update when placed in some file
        sif_file_stream = await apptainer_service.build(def_file_path)

        # TODO build image and upload

    async def batch_generate_init(
        self,
        batch_request: LLMBatchRequest[LLMResponseType],
    ) -> str:
        request_dicts = [
            {
                'request_id': str(request.id),
                'request': LLMRequestMapping[LLMResponseType].to_target(request),
            }
            for request in batch_request.requests
        ]
        lines = [
            json.dumps(request_dict, separators=(',', ':'))
            for request_dict in request_dicts
        ]
        jsonl_str = '\n'.join(lines)
        jsonl_bytes = jsonl_str.encode('utf-8')
        source = BytesStreamerUtil.stream_bytes(jsonl_bytes)

        await self.sftp_client.upload(source)

        pbs_path = self.root_path / 'huggingface_pbs.sh'
        batch_id = await self.pbs_pro_client.queue_submit(pbs_path)
        status = await self.pbs_pro_client.queue_status(batch_id)

        logger.info(f'Batch {batch_id} created with state {status.state}')

        return batch_id

    async def batch_generate_result(
        self, batch_id: str, response_type: type[LLMResponseType]
    ) -> LLMBatchResult[LLMResponseType] | None:
        status = await self.pbs_pro_client.queue_status(batch_id)

        logger.info(f'Batch {batch_id} state {status.state}')

        match status.state:
            case (
                PBSProJobState.BEGUN
                | PBSProJobState.QUEUED
                | PBSProJobState.RUNNING
                | PBSProJobState.EXITING
                | PBSProJobState.WAITING
                | PBSProJobState.TRANSITING
                | PBSProJobState.SUSPENDED
                | PBSProJobState.USER_SUSPENDED
                | PBSProJobState.HELD
                | PBSProJobState.MOVED
            ):
                return None

            case PBSProJobState.FINISHED | PBSProJobState.EXITED:
                pass

        input_path = self.root_path / f'input_{batch_id}.jsonl'
        output_path = self.root_path / f'output_{batch_id}.jsonl'

        input_file_stream = await self.sftp_client.download(input_path, None)
        output_file_stream = await self.sftp_client.download(output_path, None)

        input_stream = FileStreamerUtil.read_jsonl_file_stream(input_file_stream)
        output_stream = FileStreamerUtil.read_jsonl_file_stream(output_file_stream)

        requests_dict: dict[UUID, LLMRequest[LLMResponseType]] = {}

        async for data in input_stream:
            request_id = UUID(data['request_id'])
            request = LLMRequestMapping[LLMResponseType].to_source(
                data['request'],
                request_id=request_id,
                response_type=response_type,
            )

            requests_dict[request_id] = request

        failed_requests: list[LLMFailedRequest[LLMResponseType]] = []
        response_lists: list[LLMResponseList[LLMResponseType]] = []

        async for data in output_stream:
            request_id = UUID(data['request_id'])
            request = requests_dict[request_id]
            response = data['response']

            if response is None:
                error = LLMErrorMapping.to_source(data['error'])
                failed_request = LLMFailedRequest(
                    request=request,
                    errors=[error],
                )
                failed_requests.append(failed_request)

            else:
                completion = ChatCompletionOutput(**response)
                response_list = LLMResponseListMapping[LLMResponseType].to_source(
                    completion,
                    request_id=request_id,
                    input_id=request.params.metadata['input_id'],
                    response_type=response_type,
                )
                response_lists.append(response_list)

        batch_result = LLMBatchResult(
            response_lists=response_lists, failed_requests=failed_requests
        )

        return batch_result
