import json

from math_rag.application.models.inference import LLMBatchRequest
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.mappings.inference.openai import LLMRequestMapping


class OpenAIBatchInputFileSizeEstimator:
    @staticmethod
    def estimate(batch_request: LLMBatchRequest[LLMResponseType]):
        url = '/v1/chat/completions'
        request_dicts = [
            {
                'custom_id': str(request.id),
                'method': 'POST',
                'url': url,
                'body': LLMRequestMapping[LLMResponseType].to_target(
                    request, use_parsed=True
                ),
            }
            for request in batch_request.requests
        ]
        lines = [
            json.dumps(request_dict, separators=(',', ':'))
            for request_dict in request_dicts
        ]
        jsonl_str = '\n'.join(lines)
        jsonl_bytes = jsonl_str.encode('utf-8')
        size_in_bytes = len(jsonl_bytes)
        size_in_mb = size_in_bytes / (1024 * 1024)

        print(f'JSONL size: {size_in_bytes} bytes ({size_in_mb:.2f} MB)')
