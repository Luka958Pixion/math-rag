from datetime import timedelta

from math_rag.infrastructure.models.inference.huggingface import TGISettings


DEFAULT_TGI_SETTINGS = TGISettings(
    num_chunks=1,
    num_cpus=4,
    num_gpus=1,
    mem=32 * 1024**3,
    walltime=timedelta(minutes=120),
)

LLAMA_70B_TGI_SETTINGS = ...
