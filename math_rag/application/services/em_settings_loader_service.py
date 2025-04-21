import yaml

from decouple import UndefinedValueError, config

from math_rag.application.base.services import BaseEMSettingsLoaderService
from math_rag.application.models import (
    BatchEMSettings,
    ConcurrentEMSettings,
    EMSettings,
)


class EMSettingsLoaderService(BaseEMSettingsLoaderService):
    def __init__(self):
        self._settings = EMSettings(
            max_time=config('EM_MAX_TIME', cast=float),
            max_num_retries=config('EM_MAX_NUM_RETRIES', cast=int),
        )
        self._batch_settings = BatchEMSettings(
            poll_interval=config('BATCH_EM_POLL_INTERVAL', cast=float),
            max_num_retries=config('BATCH_EM_MAX_NUM_RETRIES', cast=int),
        )

        max_requests_per_minute = config(
            'CONCURRENT_EM_MAX_REQUESTS_PER_MINUTE',
            cast=float,  # TODO
        )
        self._concurrent_settings = ConcurrentEMSettings(
            max_requests_per_minute=config(
                'CONCURRENT_EM_MAX_REQUESTS_PER_MINUTE',
                cast=float,  # TODO
            ),
            max_tokens_per_minute=config(
                'CONCURRENT_EM_MAX_TOKENS_PER_MINUTE',
                cast=float,  # TODO
            ),
            max_num_retries=config('CONCURRENT_EM_MAX_NUM_RETRIES', cast=int),
        )

    def get_llm_setting(setting: str, model: str, cast=None, default=None):
        key = f'{setting}_{model.upper()}'

        try:
            return config(key, cast=cast)

        except UndefinedValueError:
            if default is not None:
                return default

            raise RuntimeError(f'Missing env var: {key}')

    def load_settings(self) -> EMSettings:
        return self._settings

    def load_batch_settings(self) -> BatchEMSettings:
        return self._batch_settings

    def load_concurrent_settings(self) -> ConcurrentEMSettings:
        return self._concurrent_settings
