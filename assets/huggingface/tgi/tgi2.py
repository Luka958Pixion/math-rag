import asyncio
import logging
import queue
import threading

from pathlib import Path

import backoff

from decouple import config


MAX_RETRIES = config('MAX_RETRIES', cast=int, default=3)
CONCURRENT_REQUESTS = config('CONCURRENT_REQUESTS', cast=int, default=5)
MAX_QUEUE_SIZE = 5

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def on_backoff_handler(details):
    line = details['args'][1].strip() if len(details['args']) > 1 else ''
    logger.error(
        f'Error processing line {line} (attempt {details["tries"]}/{MAX_RETRIES}): {details["exception"]}'
    )


@backoff.on_exception(
    backoff.expo,
    Exception,
    max_tries=MAX_RETRIES,
    jitter=backoff.full_jitter,
    on_backoff=on_backoff_handler,
)
async def safe_chat_completion(client, line: str) -> str:
    return await client.chat_completion(line.strip())


async def process_all_lines(lines: list, client, output_queue: queue.Queue) -> None:
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

    async def process_single_line(line: str) -> None:
        async with semaphore:
            try:
                result = await safe_chat_completion(client, line)
            except Exception as e:
                logger.error(
                    f'Failed processing line after {MAX_RETRIES} retries: {line.strip()} - Error: {e}'
                )
                result = f'Error: Failed to process line: {line.strip()}'
            # Ensure the result is pushed into the queue when space is available
            while True:
                try:
                    output_queue.put_nowait(result)
                    break
                except queue.Full:
                    await asyncio.sleep(0.1)

    try:
        async with asyncio.TaskGroup() as tg:
            for line in lines:
                tg.create_task(process_single_line(line))
    except Exception as e:
        logger.exception(f'Error in TaskGroup: {e}')


def read_inputs(input_path: Path, input_queue: queue.Queue) -> None:
    logger.info('Reader thread started.')
    try:
        with open(input_path, 'r') as infile:
            for line in infile:
                if line.strip():
                    input_queue.put(line)
        logger.info('Finished reading input file.')
    except Exception as e:
        logger.exception(f'Error reading input file: {e}')
    finally:
        input_queue.put(None)
        logger.info('Reader thread exiting.')


def process_lines(client, input_queue: queue.Queue, output_queue: queue.Queue) -> None:
    logger.info('Processor thread started.')
    lines = []
    try:
        while True:
            line = input_queue.get()
            if line is None:
                break
            lines.append(line)
        logger.info(f'Received {len(lines)} lines for processing.')
        asyncio.run(process_all_lines(lines, client, output_queue))
    except Exception as e:
        logger.exception(f'Error processing lines in asyncio loop: {e}')
    finally:
        output_queue.put(None)
        logger.info('Processor thread exiting.')


def write_outputs(output_path: Path, output_queue: queue.Queue) -> None:
    logger.info('Writer thread started.')
    try:
        with open(output_path, 'w') as outfile:
            while True:
                result = output_queue.get()
                if result is None:
                    break
                outfile.write(result + '\n')
        logger.info('Finished writing output file.')
    except Exception as e:
        logger.exception(f'Error writing output file: {e}')
    finally:
        logger.info('Writer thread exiting.')


def main():
    input_file_path = Path('path/to/input.txt')
    output_file_path = Path('path/to/output.txt')
    client = YourClient()  # Replace with your actual client initialization

    input_queue = queue.Queue(maxsize=MAX_QUEUE_SIZE)
    output_queue = queue.Queue(maxsize=MAX_QUEUE_SIZE)

    reader_thread = threading.Thread(
        target=read_inputs, args=(input_file_path, input_queue), name='ReaderThread'
    )
    processor_thread = threading.Thread(
        target=process_lines,
        args=(client, input_queue, output_queue),
        name='ProcessorThread',
    )
    writer_thread = threading.Thread(
        target=write_outputs, args=(output_file_path, output_queue), name='WriterThread'
    )

    reader_thread.start()
    processor_thread.start()
    writer_thread.start()

    reader_thread.join()
    processor_thread.join()
    writer_thread.join()
    logger.info('All threads have completed.')


if __name__ == '__main__':
    main()
