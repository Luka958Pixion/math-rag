import json

from asyncio import Semaphore, TaskGroup, run, sleep
from logging import INFO, basicConfig, getLogger
from pathlib import Path
from queue import Full, Queue
from threading import Thread

from backoff import expo, full_jitter, on_exception
from decouple import config
from huggingface_hub import AsyncInferenceClient
from huggingface_hub.errors import TextGenerationError


DEPLOYMENT = config('DEPLOYMENT', default='develop')

# develop
TGI_API_KEY = config('TGI_API_KEY', default=None)
MODEL_HUB_ID = config('MODEL_HUB_ID', default=None)

# production
WORKDIR = config('PBS_O_WORKDIR', cast=Path, default=Path.cwd())
TGI_BASE_URL = config('TGI_BASE_URL', default=None)

MAX_RETRIES = config('MAX_RETRIES', cast=int, default=3)

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
    output = await client.chat_completion(**request['request'])
    response = {'request_id': request['request_id'], 'response': output, 'error': None}

    return response


async def process_input_line(
    semaphore: Semaphore,
    input_line: str,
    client: AsyncInferenceClient,
    output_queue: Queue[str | None],
):
    async with semaphore:
        request = json.loads(input_line)

        try:
            response = await safe_chat_completion(client, request)

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
                output_queue.put_nowait(output_line)
                break

            except Full:
                await sleep(0.1)


async def process_input_lines(
    input_lines: list[str],
    client: AsyncInferenceClient,
    output_queue: Queue[str | None],
):
    semaphore = Semaphore(MAX_CONCURRENT_REQUESTS)

    try:
        async with TaskGroup() as task_group:
            for input_line in input_lines:
                task_group.create_task(
                    process_input_line(semaphore, input_line, client, output_queue)
                )

    except Exception as e:
        logger.exception(f'Error in TaskGroup: {e}')


def read_input_file(input_file_path: Path, input_queue: Queue[str | None]):
    logger.info('Reader thread started')

    try:
        with open(input_file_path, 'r') as input_file:
            for line in input_file:
                line = line.strip()

                if line:
                    input_queue.put(line)

        logger.info('Finished reading input file')

    except Exception as e:
        logger.exception(f'Error reading input file: {e}')

    finally:
        input_queue.put(None)
        logger.info('Reader thread exiting')


def process_lines(client, input_queue: Queue[str], output_queue: Queue[str | None]):
    logger.info('Processor thread started')

    try:
        input_lines: list[str] = []

        while True:
            input_line = input_queue.get()

            if input_line is None:
                break

            input_lines.append(input_line)

        run(process_input_lines(input_lines, client, output_queue))

    except Exception as e:
        logger.exception(f'Error processing lines in asyncio loop: {e}')

    finally:
        output_queue.put(None)
        logger.info('Processor thread exiting')


def write_output_file(output_file_path: Path, output_queue: Queue[str | None]):
    logger.info('Writer thread started')

    try:
        with open(output_file_path, 'w') as output_file:
            while True:
                line = output_queue.get()

                if line is None:
                    break

                output_file.write(line + '\n')

        logger.info('Finished writing output file')

    except Exception as e:
        logger.exception(f'Error writing output file: {e}')

    finally:
        logger.info('Writer thread exiting')


def main():
    input_file_path = WORKDIR / 'input.jsonl'
    output_file_path = WORKDIR / 'output.jsonl'

    client = AsyncInferenceClient(
        base_url=TGI_BASE_URL,
        api_key=TGI_API_KEY,
        model=MODEL_HUB_ID,
        provider='hf-inference',
        timeout=None,
    )

    input_queue: Queue[str | None] = Queue(maxsize=MAX_CONCURRENT_REQUESTS)
    output_queue: Queue[str | None] = Queue(maxsize=MAX_CONCURRENT_REQUESTS)

    reader_thread = Thread(
        target=read_input_file, args=(input_file_path, input_queue), name='ReaderThread'
    )
    processor_thread = Thread(
        target=process_lines,
        args=(client, input_queue, output_queue),
        name='ProcessorThread',
    )
    writer_thread = Thread(
        target=write_output_file,
        args=(output_file_path, output_queue),
        name='WriterThread',
    )

    reader_thread.start()
    processor_thread.start()
    writer_thread.start()

    reader_thread.join()
    processor_thread.join()
    writer_thread.join()

    logger.info('All threads have completed')


if __name__ == '__main__':
    main()
