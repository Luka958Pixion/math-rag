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


MAX_QUEUE_SIZE = 5
MAX_RETRIES = config('MAX_RETRIES', cast=int, default=3)
CONCURRENT_REQUESTS = config('CONCURRENT_REQUESTS', cast=int, default=5)
ROOT = config('ROOT', cast=Path, default=...)  # TODO /lustre/user...
TGI_BASE_URL = config('TGI_BASE_URL')


basicConfig(
    level=INFO, format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s'
)
logger = getLogger(__name__)


def on_backoff_handler(details: dict):
    line = details['args'][1].strip() if len(details['args']) > 1 else ''
    logger.error(
        f'Error processing line {line} '
        f'(attempt {details['tries']}/{MAX_RETRIES}): '
        f'{details['exception']}'
    )


@on_exception(
    expo,
    TextGenerationError,
    max_tries=MAX_RETRIES,
    jitter=full_jitter,
    on_backoff=on_backoff_handler,
)
async def safe_chat_completion(client: AsyncInferenceClient, input_line: str) -> str:
    request = json.loads(input_line.strip())
    output = await client.chat_completion(**request['body'])
    response = {'request_id': request['id'], 'body': output}
    output_line = json.dumps(response)

    return output_line


async def process_all_lines(lines: list[str], client, output_queue: Queue):
    semaphore = Semaphore(CONCURRENT_REQUESTS)

    async def process_single_line(line: str):
        async with semaphore:
            try:
                result = await safe_chat_completion(client, line)

            except Exception as e:
                logger.error(
                    f'Failed processing line after {MAX_RETRIES} retries: '
                    f'{line.strip()} - Error: {e}'
                )
                result = f'Error: Failed to process line: {line.strip()}'

            while True:
                try:
                    output_queue.put_nowait(result)
                    break

                except Full:
                    await sleep(0.1)

    try:
        async with TaskGroup() as tg:
            for line in lines:
                tg.create_task(process_single_line(line))

    except Exception as e:
        logger.exception(f'Error in TaskGroup: {e}')


def read_input_file(input_path: Path, input_queue: Queue):
    logger.info('Reader thread started')

    try:
        with open(input_path, 'r') as infile:
            for line in infile:
                if line.strip():
                    input_queue.put(line)

        logger.info('Finished reading input file')

    except Exception as e:
        logger.exception(f'Error reading input file: {e}')

    finally:
        input_queue.put(None)
        logger.info('Reader thread exiting')


def process_lines(client, input_queue: Queue, output_queue: Queue):
    logger.info('Processor thread started')

    try:
        lines: list[str] = []

        while True:
            line = input_queue.get()

            if line is None:
                break

            lines.append(line)

        run(process_all_lines(lines, client, output_queue))

    except Exception as e:
        logger.exception(f'Error processing lines in asyncio loop: {e}')

    finally:
        output_queue.put(None)
        logger.info('Processor thread exiting')


def write_output_path(output_path: Path, output_queue: Queue):
    logger.info('Writer thread started')

    try:
        with open(output_path, 'w') as outfile:
            while True:
                line = output_queue.get()

                if line is None:
                    break

                outfile.write(line + '\n')

        logger.info('Finished writing output file')

    except Exception as e:
        logger.exception(f'Error writing output file: {e}')

    finally:
        logger.info('Writer thread exiting')


def main():
    input_file_path = Path('path/to/input.txt')
    output_file_path = Path('path/to/output.txt')

    client = AsyncInferenceClient()

    input_queue = Queue(maxsize=MAX_QUEUE_SIZE)
    output_queue = Queue(maxsize=MAX_QUEUE_SIZE)

    reader_thread = Thread(
        target=read_input_file, args=(input_file_path, input_queue), name='ReaderThread'
    )
    processor_thread = Thread(
        target=process_lines,
        args=(client, input_queue, output_queue),
        name='ProcessorThread',
    )
    writer_thread = Thread(
        target=write_output_path,
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
