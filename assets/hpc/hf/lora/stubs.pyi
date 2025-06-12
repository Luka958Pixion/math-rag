from typing import Any, Protocol

from transformers.modeling_utils import PreTrainedModel
from transformers.tokenization_utils_fast import PreTrainedTokenizerFast

class ModelSpec(Protocol):
    def init_tokenizer(self, tokenizer: PreTrainedTokenizerFast) -> PreTrainedTokenizerFast: ...
    def init_language_model(self, model: PreTrainedModel) -> PreTrainedModel: ...
    def format_prompt(
        sample: dict[str, str], prompt_collection: dict[str, Any]
    ) -> dict[str, Any]: ...
    def formatting_func(
        tokenizer: PreTrainedTokenizerFast, batch: dict[str, Any]
    ) -> dict[str, Any]: ...
