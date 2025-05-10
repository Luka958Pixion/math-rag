import asyncio
import json

from logging import INFO, basicConfig, getLogger
from pathlib import Path
from queue import Full, Queue
from threading import Thread
from uuid import UUID

from backoff import expo, full_jitter, on_exception
from decouple import Config, RepositoryEnv
from huggingface_hub import AsyncInferenceClient
from huggingface_hub.errors import TextGenerationError


config = Config(repository=RepositoryEnv('.env.hpc.hf.tgi'))

# NOTE: running locally requires TGI_BASE_URL
# NOTE: running remotely requires TGI_API_KEY and MODEL_HUB_ID
TGI_BASE_URL = config('TGI_BASE_URL', default=None)
TGI_API_KEY = config('TGI_API_KEY', default=None)
MODEL_HUB_ID = config('MODEL_HUB_ID', default=None)
BATCH_REQUEST_ID = config('BATCH_REQUEST_ID', cast=UUID)
WORKDIR = config('PBS_O_WORKDIR', cast=Path)

MAX_RETRIES = 3
MAX_CONCURRENT_REQUESTS = 128  # max for TGI


basicConfig(
    level=INFO, format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s'
)
logger = getLogger(__name__)


def on_backoff_handler(details: dict):
    line = details['args'][1] if len(details['args']) > 1 else str()
    retries = details['tries']
    exception = details['exception']
    logger.error(
        f'Error processing line {line} '
        f'(attempt {retries}/{MAX_RETRIES}): '
        f'{exception}'
    )


@on_exception(
    expo,
    TextGenerationError,
    max_tries=MAX_RETRIES,
    jitter=full_jitter,
    on_backoff=on_backoff_handler,
)
async def safe_chat_completion(client: AsyncInferenceClient, request: dict) -> dict:
    if TGI_BASE_URL:
        request['request'].pop('model')

    output = await client.chat_completion(**request['request'])
    response = {'request_id': request['request_id'], 'response': output, 'error': None}

    return response


class ReaderThread(Thread):
    def __init__(self, input_file_path: Path, input_queue: Queue[str | None]):
        super().__init__(name=self.__class__.__name__)

        self._input_file_path = input_file_path
        self._input_queue = input_queue

    def run(self):
        logger.info(f'{self.__class__.__name__} started')

        try:
            with open(self._input_file_path, 'r') as input_file:
                for line in input_file:
                    line = line.strip()

                    if line:
                        self._input_queue.put(line)

            logger.info('Finished reading input file')

        except Exception as e:
            logger.exception(f'Error reading input file: {e}')

        finally:
            self._input_queue.put(None)
            logger.info(f'{self.__class__.__name__} exited')


class ProcessorThread(Thread):
    def __init__(
        self,
        client: AsyncInferenceClient,
        input_queue: Queue[str],
        output_queue: Queue[str | None],
    ):
        super().__init__(name=self.__class__.__name__)

        self._client = client
        self._input_queue = input_queue
        self._output_queue = output_queue

    def run(self):
        logger.info(f'{self.__class__.__name__} started')

        try:
            input_lines: list[str] = []

            while True:
                input_line = self._input_queue.get()

                if input_line is None:
                    break

                input_lines.append(input_line)

            asyncio.run(self._process_input_lines(input_lines))

        except Exception as e:
            logger.exception(f'Error processing lines in asyncio loop: {e}')

        finally:
            self._output_queue.put(None)
            logger.info(f'{self.__class__.__name__} exited')

    async def _process_input_lines(self, input_lines: list[str]):
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

        try:
            async with asyncio.TaskGroup() as task_group:
                for input_line in input_lines:
                    task_group.create_task(
                        self._process_input_line(semaphore, input_line)
                    )

        except Exception as e:
            logger.exception(f'Error in TaskGroup: {e}')

    async def _process_input_line(
        self,
        semaphore: asyncio.Semaphore,
        input_line: str,
    ):
        async with semaphore:
            request = json.loads(input_line)

            try:
                response = await safe_chat_completion(self._client, request)

            except Exception as e:
                logger.error(
                    f'Failed processing line after {MAX_RETRIES} retries: '
                    f'{input_line} - Error: {e}'
                )
                response = {
                    'request_id': request['request_id'],
                    'response': None,
                    'error': e,
                }

            finally:
                output_line = json.dumps(response)

            while True:
                try:
                    self._output_queue.put_nowait(output_line)
                    break

                except Full:
                    await asyncio.sleep(0.1)


class WriterThread(Thread):
    def __init__(self, output_file_path: Path, output_queue: Queue[str | None]):
        super().__init__(name=self.__class__.__name__)

        self._output_file_path = output_file_path
        self._output_queue = output_queue

    def run(self):
        logger.info(f'{self.__class__.__name__} started')

        try:
            with open(self._output_file_path, 'w') as output_file:
                while True:
                    line = self._output_queue.get()

                    if line is None:
                        break

                    output_file.write(line + '\n')

            logger.info('Finished writing output file')

        except Exception as e:
            logger.exception(f'Error writing output file: {e}')

        finally:
            logger.info(f'{self.__class__.__name__} exited')


def main():
    input_file_path = WORKDIR / f'input_{BATCH_REQUEST_ID}.jsonl'
    output_file_path = WORKDIR / f'output_{BATCH_REQUEST_ID}.jsonl'

    client = AsyncInferenceClient(
        base_url=TGI_BASE_URL,
        api_key=TGI_API_KEY,
        model=MODEL_HUB_ID,
        timeout=None,
    )

    input_queue: Queue[str | None] = Queue(maxsize=MAX_CONCURRENT_REQUESTS)
    output_queue: Queue[str | None] = Queue(maxsize=MAX_CONCURRENT_REQUESTS)

    reader_thread = ReaderThread(input_file_path, input_queue)
    processor_thread = ProcessorThread(client, input_queue, output_queue)
    writer_thread = WriterThread(output_file_path, output_queue)

    reader_thread.start()
    processor_thread.start()
    writer_thread.start()

    reader_thread.join()
    processor_thread.join()
    writer_thread.join()

    logger.info('All threads have exited')


if __name__ == '__main__':
    main()
