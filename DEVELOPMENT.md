# math-rag

## Testing
- `pytest -s tests/infrastructure/inference/huggingface/test_tgi_batch_llm.py`

## Requirements
`requirements.txt` for `tgi.py` is exported using:

`poetry export --only dev.tgi --without-hashes --format requirements.txt --output ./assets/hpc/hf/tgi/requirements.txt`