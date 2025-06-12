# https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct
import json

from typing import Any, cast

from transformers.models.llama.configuration_llama import LlamaConfig
from transformers.models.llama.modeling_llama import LlamaForCausalLM
from transformers.models.llama.tokenization_llama_fast import LlamaTokenizerFast


def init_tokenizer(tokenizer: LlamaTokenizerFast):
    tokenizer.add_special_tokens(
        {
            'additional_special_tokens': ['<|system|>', '<|user|>', '<|assistant|>', '<|end|>'],
            'pad_token': '<PAD>',
        }
    )
    tokenizer.padding_side = 'left'

    return tokenizer


def init_language_model(model: LlamaForCausalLM):
    assert isinstance(model.config, LlamaConfig)

    model.config.use_cache = False
    model.config.pretraining_tp = 1

    return model


def format_prompt(sample: dict[str, str], prompt_collection: dict[str, Any]) -> dict[str, Any]:
    """
    Returns a dict with a single key 'messages':
    {
        'messages': [
            {
                'role': 'system',
                'content': ...
            },
            {
                'role': 'user',
                'content': ...
            },
            {
                'role': 'assistant',
                'content': '{"label": "..."}'
            }
        ]
    }
    """
    system_prompt = prompt_collection.get('system')
    system_prompt_template = cast(str, system_prompt['template'])
    system_message_content = system_prompt_template.format()

    user_prompt = prompt_collection.get('user')
    user_prompt_template = cast(str, user_prompt['template'])
    user_message_content = user_prompt_template.format(
        **{input_key: sample[input_key] for input_key in prompt_collection.get('input_keys')}
    )

    assistant_message_content = json.dumps({'label': sample['label']})

    return {
        'messages': [
            {'role': 'system', 'content': system_message_content},
            {'role': 'user', 'content': user_message_content},
            {'role': 'assistant', 'content': assistant_message_content},
        ]
    }


def formatting_func(tokenizer: LlamaTokenizerFast, batch: dict[str, Any]) -> dict[str, Any]:
    """
    Expects batch['messages'] as a list of lists of dicts:
    [
        [
            {
                'role': 'system',
                'content': ...
            },
            {
                'role':'user',
                'content': ...
            },
            {
                'role': 'assistant',
                'content': ...
            }
        ]
    ]
    Returns a dict with 'input_ids', 'attention_mask', and 'labels'.
    """
    input_token_ids = [
        tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False,
        )
        for messages in batch['messages']
    ]
    tokenized = tokenizer(input_token_ids, truncation=True, max_length=512, padding='max_length')
    tokenized['labels'] = tokenized['input_ids'].copy()

    return tokenized
