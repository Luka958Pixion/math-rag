from asyncio import Queue, create_task, sleep
from collections import deque
from logging import getLogger
from time import ctime, perf_counter

from openai import AsyncOpenAI, RateLimitError

from math_rag.application.base.inference import BaseConcurrentEM
from math_rag.application.models.inference import (
    EMConcurrentRequest,
    EMConcurrentResult,
    EMError,
    EMFailedRequest,
    EMRequest,
    EMRequestTracker,
    EMResponseList,
    EMStatusTracker,
)
from math_rag.infrastructure.constants.inference.openai import (
    CONCURRENT_WAIT_AFTER_RATE_LIMIT_ERROR,
    CONCURRENT_WAIT_IDLE,
    OPENAI_ERRORS_TO_RAISE,
    OPENAI_ERRORS_TO_RETRY_NO_RATE_LIMIT,
)
from math_rag.infrastructure.mappings.inference.openai import (
    EMRequestMapping,
    EMResponseListMapping,
)
from math_rag.infrastructure.utils import TokenCounterUtil


logger = getLogger(__name__)


class OpenAIConcurrentEM(BaseConcurrentEM):
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    async def _embed(
        self,
        request_tracker: EMRequestTracker,
        retry_queue: Queue[EMRequestTracker],
        status_tracker: EMStatusTracker,
        response_lists: list[EMResponseList],
        failed_requests: list[EMFailedRequest],
    ):
        request = request_tracker.request
        exception = None

        try:
            request_dict = EMRequestMapping.to_target(request)
            create_embedding_response = await self.client.embeddings.create(
                **request_dict
            )
            response_list = EMResponseListMapping.to_source(
                create_embedding_response,
                request_id=request.id,
            )

        except RateLimitError as e:
            exception = e
            status_tracker.time_of_last_rate_limit_error = perf_counter()
            status_tracker.num_rate_limit_errors += 1

        except OPENAI_ERRORS_TO_RETRY_NO_RATE_LIMIT as e:
            exception = e
            status_tracker.num_api_errors += 1

        except (*OPENAI_ERRORS_TO_RAISE, Exception) as e:
            logger.error(f'Uncaught exception {type(e).__class__}: {e}')

            raise

        if exception:
            error = EMError(message=exception.message, body=exception.message)
            request_tracker.errors.append(error)

            if request_tracker.retries_left:
                retry_queue.put_nowait(request_tracker)

            else:
                failed_request = EMFailedRequest(
                    request=request_tracker.request, errors=request_tracker.errors
                )
                failed_requests.append(failed_request)

                status_tracker.num_tasks_in_progress -= 1
                status_tracker.num_tasks_failed += 1

                logger.error(
                    f'Request {request_tracker.request.id} failed after all retries'
                )

        else:
            response_lists.append(response_list)

            status_tracker.num_tasks_in_progress -= 1
            status_tracker.num_tasks_succeeded += 1

    async def concurrent_embed(
        self,
        concurrent_request: EMConcurrentRequest,
        *,
        max_requests_per_minute: float,
        max_tokens_per_minute: float,
        max_num_retries: int,
    ) -> EMConcurrentResult:
        retry_queue: Queue[EMRequestTracker] = Queue()
        status_tracker = EMStatusTracker()
        next_request: EMRequestTracker | None = None

        available_request_capacity = max_requests_per_minute
        available_token_capacity = max_tokens_per_minute
        last_update_time = perf_counter()

        requests_not_empty = True

        requests: deque[EMRequest] = deque(concurrent_request.requests)
        response_lists: list[EMResponseList] = []
        failed_requests: list[EMFailedRequest] = []

        while True:
            if next_request is None:
                if not retry_queue.empty():
                    next_request = retry_queue.get_nowait()
                    logger.debug(f'Retrying request {next_request.request.id}')

                elif requests_not_empty:
                    if requests:
                        request = requests.popleft()
                        token_consumption = TokenCounterUtil.count(request)
                        next_request = EMRequestTracker(
                            request=request,
                            token_consumption=token_consumption,
                            retries_left=max_num_retries,
                        )
                        status_tracker.num_tasks_started += 1
                        status_tracker.num_tasks_in_progress += 1

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
                    next_request.retries_left -= 1

                    create_task(
                        self._embed(
                            request_tracker=next_request,
                            retry_queue=retry_queue,
                            status_tracker=status_tracker,
                            response_lists=response_lists,
                            failed_requests=failed_requests,
                        )
                    )
                    next_request = None

            if status_tracker.num_tasks_in_progress == 0:
                break

            await sleep(CONCURRENT_WAIT_IDLE)

            seconds_since_rate_limit_error = (
                perf_counter() - status_tracker.time_of_last_rate_limit_error
            )

            if seconds_since_rate_limit_error < CONCURRENT_WAIT_AFTER_RATE_LIMIT_ERROR:
                remaining_seconds_to_pause = (
                    CONCURRENT_WAIT_AFTER_RATE_LIMIT_ERROR
                    - seconds_since_rate_limit_error
                )
                await sleep(remaining_seconds_to_pause)

                wait_until = ctime(
                    status_tracker.time_of_last_rate_limit_error
                    + CONCURRENT_WAIT_AFTER_RATE_LIMIT_ERROR
                )
                logger.warning(f'Pausing to cool down until {wait_until}')

        if status_tracker.num_tasks_failed > 0:
            logger.warning(
                f'{status_tracker.num_tasks_failed} / '
                f'{status_tracker.num_tasks_started} requests failed'
            )

        if status_tracker.num_rate_limit_errors > 0:
            logger.warning(
                f'{status_tracker.num_rate_limit_errors} rate limit errors received'
            )

        concurrent_result = EMConcurrentResult(
            concurrent_request_id=concurrent_request.id,
            response_lists=response_lists,
            failed_requests=failed_requests,
        )

        return concurrent_result
