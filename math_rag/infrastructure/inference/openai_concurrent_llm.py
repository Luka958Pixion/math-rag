import logging

from asyncio import Queue, create_task, sleep
from collections import deque
from time import ctime, perf_counter

from openai import AsyncOpenAI, RateLimitError
from tiktoken import get_encoding

from math_rag.application.base.inference import BaseConcurrentLLM
from math_rag.application.models.inference import (
    LLMRequest,
    LLMRequestBatch,
    LLMRequestTracker,
    LLMResponseBatch,
    LLMResponseList,
    LLMStatusTracker,
    LLMTextResponse,
)
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.inference.constants import (
    ENCODING_NAME,
    MAX_COMPLETION_TOKENS,
    OPENAI_ERRORS_TO_RAISE,
    OPENAI_ERRORS_TO_RETRY_NO_RATE_LIMIT,
    SECONDS_TO_PAUSE_AFTER_RATE_LIMIT_ERROR,
    SECONDS_TO_SLEEP_EACH_LOOP,
)
from math_rag.infrastructure.mappings.inference import LLMResponseListMapping


class OpenAIConcurrentLLM(BaseConcurrentLLM):
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    async def _generate_text(
        self,
        request: LLMRequest[LLMResponseType],
    ) -> LLMResponseList[LLMResponseType]:
        params = request.params
        completion = await self.client.chat.completions.create(
            model=params.model,
            messages=[
                {'role': message.role, 'content': message.content}
                for message in request.conversation.messages
            ],
            response_format={'type': 'text'},
            temperature=params.temperature,
            logprobs=params.top_logprobs is not None,
            top_logprobs=params.top_logprobs,
            reasoning_effort=params.reasoning_effort,
        )
        response_list = LLMResponseListMapping[LLMResponseType].to_source(completion)

        return response_list

    async def _generate_json(
        self,
        request: LLMRequest[LLMResponseType],
    ) -> LLMResponseList[LLMResponseType]:
        params = request.params
        parsed_completion = await self.client.beta.chat.completions.parse(
            model=params.model,
            messages=[
                {'role': message.role, 'content': message.content}
                for message in request.conversation.messages
            ],
            response_format=params.response_type,
            temperature=params.temperature,
            logprobs=params.top_logprobs is not None,
            top_logprobs=params.top_logprobs,
            reasoning_effort=params.reasoning_effort,
        )
        response_list = LLMResponseListMapping[LLMResponseType].to_source(
            parsed_completion
        )

        return response_list

    async def _generate(
        self,
        request_tracker: LLMRequestTracker[LLMResponseType],
        retry_queue: Queue[LLMRequestTracker[LLMResponseType]],
        status_tracker: LLMStatusTracker,
        response_lists: list[LLMResponseList[LLMResponseType]],
    ):
        error = None

        try:
            request = request_tracker.request
            response_list = (
                await self._generate_text(request)
                if request.params.response_type is LLMTextResponse
                else await self._generate_json(request)
            )

        except RateLimitError as e:
            error = e
            status_tracker.time_of_last_rate_limit_error = perf_counter()
            status_tracker.num_rate_limit_errors += 1

        except OPENAI_ERRORS_TO_RETRY_NO_RATE_LIMIT as e:
            error = e
            status_tracker.num_api_errors += 1

        except OPENAI_ERRORS_TO_RAISE:
            raise

        if error:
            request_tracker.errors.append(error)

            if request_tracker.attempts_left:
                retry_queue.put_nowait(request_tracker)

            else:
                logging.error(f'Request {request_tracker.id} failed after all attempts')
                # TODO: save self.errors

                status_tracker.num_tasks_in_progress -= 1
                status_tracker.num_tasks_failed += 1
        else:
            response_lists.append(response_list)

            status_tracker.num_tasks_in_progress -= 1
            status_tracker.num_tasks_succeeded += 1

    def num_tokens_from_request(self, request: LLMRequest[LLMResponseType]):
        encoding = get_encoding(ENCODING_NAME)
        prompt_tokens = 0

        for message in request.conversation.messages:
            message_content_tokens = encoding.encode(message.content)
            prompt_tokens += len(message_content_tokens)
            prompt_tokens += 4  # TODO why

        prompt_tokens += 2  # TODO why

        max_completion_tokens = (
            request.params.max_completion_tokens or MAX_COMPLETION_TOKENS
        )
        n = request.params.n
        completion_tokens = n * max_completion_tokens

        total_tokens = prompt_tokens + completion_tokens

        return total_tokens

    async def concurrent_generate(
        self,
        request_batch: LLMRequestBatch[LLMResponseType],
        max_requests_per_minute: float,
        max_tokens_per_minute: float,
        max_attempts: int,
    ) -> LLMResponseBatch[LLMResponseType]:
        retry_queue: Queue[LLMRequestTracker] = Queue()
        status_tracker = LLMStatusTracker()
        next_request: LLMRequestTracker | None = None

        available_request_capacity = max_requests_per_minute
        available_token_capacity = max_tokens_per_minute
        last_update_time = perf_counter()

        requests_not_empty = True

        requests: deque[LLMRequest[LLMResponseType]] = deque(request_batch.requests)
        response_lists: list[LLMResponseList[LLMResponseType]] = []

        while True:
            if next_request is None:
                if not retry_queue.empty():
                    next_request = retry_queue.get_nowait()
                    logging.debug(f'Retrying request {next_request.request.id}')

                elif requests_not_empty:
                    if requests:
                        request = requests.popleft()
                        token_consumption = self.num_tokens_from_request(request)
                        next_request = LLMRequestTracker(
                            request=request,
                            token_consumption=token_consumption,
                            attempts_left=max_attempts,
                        )
                        status_tracker.num_tasks_started += 1
                        status_tracker.num_tasks_in_progress += 1
                        logging.debug(f'Reading request {next_request.request.id}')

                    else:
                        requests_not_empty = False

            current_time = perf_counter()
            seconds_since_update = current_time - last_update_time
            available_request_capacity = min(
                available_request_capacity
                + max_requests_per_minute * seconds_since_update / 60.0,
                max_requests_per_minute,
            )
            available_token_capacity = min(
                available_token_capacity
                + max_tokens_per_minute * seconds_since_update / 60.0,
                max_tokens_per_minute,
            )
            last_update_time = current_time

            if next_request:
                next_request_tokens = next_request.token_consumption

                if (
                    available_request_capacity >= 1
                    and available_token_capacity >= next_request_tokens
                ):
                    available_request_capacity -= 1
                    available_token_capacity -= next_request_tokens
                    next_request.attempts_left -= 1

                    create_task(
                        self._generate(
                            request_tracker=next_request,
                            retry_queue=retry_queue,
                            status_tracker=status_tracker,
                            response_lists=response_lists,
                        )
                    )
                    next_request = None

            if status_tracker.num_tasks_in_progress == 0:
                break

            await sleep(SECONDS_TO_SLEEP_EACH_LOOP)
            seconds_since_rate_limit_error = (
                perf_counter() - status_tracker.time_of_last_rate_limit_error
            )

            if seconds_since_rate_limit_error < SECONDS_TO_PAUSE_AFTER_RATE_LIMIT_ERROR:
                remaining_seconds_to_pause = (
                    SECONDS_TO_PAUSE_AFTER_RATE_LIMIT_ERROR
                    - seconds_since_rate_limit_error
                )
                await sleep(remaining_seconds_to_pause)

                logging.warning(
                    f'Pausing to cool down until {ctime(status_tracker.time_of_last_rate_limit_error + SECONDS_TO_PAUSE_AFTER_RATE_LIMIT_ERROR)}'
                )

        if status_tracker.num_tasks_failed > 0:
            logging.warning(
                f'{status_tracker.num_tasks_failed} / {status_tracker.num_tasks_started} requests failed'
            )

        if status_tracker.num_rate_limit_errors > 0:
            logging.warning(
                f'{status_tracker.num_rate_limit_errors} rate limit errors received'
            )

        response_batch = LLMResponseBatch(
            incomplete_request_batch=...,  # TODO not needed
            response_lists=response_lists,
        )

        return response_batch
