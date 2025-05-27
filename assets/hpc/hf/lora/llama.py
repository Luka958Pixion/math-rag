from transformers.models.llama.configuration_llama import LlamaConfig
from transformers.models.llama.modeling_llama import LlamaForCausalLM
from transformers.models.llama.tokenization_llama_fast import LlamaTokenizerFast


def init_llama_tokenizer(tokenizer: LlamaTokenizerFast):
    # tokenizer.pad_token = '<PAD>'
    tokenizer.add_special_tokens({'pad_token': '<PAD>'})
    tokenizer.padding_side = 'left'
    tokenizer.chat_template = (
        "{% for message in messages %}{{ message['role'] }}: {{ message['content'] }}\n{% endfor %}"
    )

    return tokenizer


def init_llama_language_model(model: LlamaForCausalLM):
    assert isinstance(model.config, LlamaConfig)

    model.config.use_cache = False
    model.config.pretraining_tp = 1

    return model
