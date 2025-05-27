from transformers.models.llama.tokenization_llama import LlamaTokenizer
from transformers.models.phi3.configuration_phi3 import Phi3Config
from transformers.models.phi3.modeling_phi3 import Phi3ForCausalLM


def init_phi3_tokenizer(tokenizer: LlamaTokenizer):
    # NOTE: phi3 is using llama tokenizer
    # tokenizer.pad_token = '<PAD>'
    tokenizer.add_special_tokens({'pad_token': '<PAD>'})
    tokenizer.padding_side = 'left'
    tokenizer.chat_template = (
        "{% for message in messages %}{{ message['role'] }}: {{ message['content'] }}\n{% endfor %}"
    )

    return tokenizer


def init_phi3_language_model(model: Phi3ForCausalLM):
    assert isinstance(model.config, Phi3Config)

    model.config.use_cache = False
    model.config.pretraining_tp = 1

    return model
