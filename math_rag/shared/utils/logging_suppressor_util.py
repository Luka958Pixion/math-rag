import logging

from contextlib import contextmanager


class LoggingSuppressorUtil:
    @staticmethod
    @contextmanager
    def suppress(logger_name: str):
        logger = logging.getLogger(logger_name)
        original_level = logger.level
        logger.setLevel(logging.CRITICAL + 1)

        try:
            yield

        finally:
            logger.setLevel(original_level)
