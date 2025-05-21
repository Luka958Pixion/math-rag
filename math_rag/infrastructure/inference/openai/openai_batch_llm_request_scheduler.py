from datetime import date

from math_rag.application.base.inference import BaseBatchLLMRequestScheduler
from math_rag.application.models.inference import (
    LLMBatchRequest,
    LLMBatchRequestSchedule,
)
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.constants.inference.openai import (
    BATCH_INPUT_FILE_SIZE_LIMIT,
    BATCH_INPUT_FILE_SIZE_LIMIT_SCALED,
)
from math_rag.infrastructure.utils import LLMTokenCounterUtil


class OpenAIBatchLLMRequestScheduler(BaseBatchLLMRequestScheduler):
    async def schedule(
        self,
        batch_request: LLMBatchRequest[LLMResponseType],
        *,
        max_tokens_per_day: float | None,
        max_input_file_size: int | None,
    ) -> LLMBatchRequestSchedule[LLMResponseType]:
        token_counts = LLMTokenCounterUtil.batch_count(batch_request)

    async def helper(self):
        MAX_TOKENS_PER_DAY = 1000000  # e.g., total tokens allowed per day
        MAX_FILE_SIZE_BYTES = 4 * 1024 * 1024  # e.g., 4 MB upload limit

        # Input/Output paths:
        INPUT_FILE = 'requests.json'  # Path to your full list of requests
        OUTPUT_DIR = 'batches'  # Directory to write sub-batch files
        SCHEDULE_MAP_FILE = (
            'batch_schedule.json'  # Mapping of batch file to its timestamp
        )

        # Starting schedule timestamp (as early as possible):
        # By default, use current local time. Adjust if you need to align with UTC or specific hour.
        start_time = datetime.now()

        # ------------------------------------------
        # PREPARATION
        # ------------------------------------------
        # Ensure output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # Load all requests
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            all_requests = json.load(f)

        # Initialize tokenizer for your model
        # Replace 'gpt-4' with the model you use for accurate token counts
        encoding = tiktoken.encoding_for_model('gpt-4')

        # ------------------------------------------
        # SPLIT INTO SUB-BATCHES
        # ------------------------------------------
        batch_index = 0
        current_tokens = 0
        current_size = 0
        current_batch = []
        schedule_time = start_time
        schedule_map = []

        for req in all_requests:
            # Serialize request to JSON to estimate size
            req_json = json.dumps(req, ensure_ascii=False)
            req_size = len(req_json.encode('utf-8'))

            # Estimate token count of the prompt/text in the request
            # Adjust if your payload has different structure
            prompt_text = req.get('prompt', req_json)
            req_tokens = len(encoding.encode(prompt_text))

            # Check if adding this request would exceed limits
            exceeds_tokens = (current_tokens + req_tokens) > MAX_TOKENS_PER_DAY
            exceeds_size = (current_size + req_size) > MAX_FILE_SIZE_BYTES

            if current_batch and (exceeds_tokens or exceeds_size):
                # Write out the current batch
                batch_index += 1
                filename = f'batch_{batch_index:03d}.json'
                out_path = os.path.join(OUTPUT_DIR, filename)
                with open(out_path, 'w', encoding='utf-8') as out_f:
                    json.dump(current_batch, out_f, ensure_ascii=False, indent=2)

                # Record its scheduled timestamp
                schedule_map.append(
                    {'file': filename, 'schedule': schedule_time.isoformat()}
                )

                # Prepare next batch: reset counters & batch list
                schedule_time += timedelta(days=1)
                current_batch = []
                current_tokens = 0
                current_size = 0

            # Add the request to the batch
            current_batch.append(req)
            current_tokens += req_tokens
            current_size += req_size

        # Write final batch if any
        if current_batch:
            batch_index += 1
            filename = f'batch_{batch_index:03d}.json'
            out_path = os.path.join(OUTPUT_DIR, filename)
            with open(out_path, 'w', encoding='utf-8') as out_f:
                json.dump(current_batch, out_f, ensure_ascii=False, indent=2)
            schedule_map.append(
                {'file': filename, 'schedule': schedule_time.isoformat()}
            )
