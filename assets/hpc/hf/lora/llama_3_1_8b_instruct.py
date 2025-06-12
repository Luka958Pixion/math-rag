# https://huggingface.co/meta-llama/Llama-3.1-8B
import json

from typing import Any

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


def format_prompt(sample: dict[str, str], prompt: dict[str, Any]) -> dict[str, Any]:
    """
    1. Splits prompt['template'] at '### LaTeX:' so that
       - everything before '### LaTeX:' becomes the system prompt
       - '### LaTeX:\n{latex}\n\n### Class:' becomes the user prompt (with {latex} filled in)
    2. Creates an `assistant` message whose content is exactly {'label':'<ground_truth>'}.

    Returns a dict with a single key 'messages', e.g.:
        { 'messages': [ {'role':'system', 'content':…},
                        {'role':'user',   'content':…},
                        {'role':'assistant','content':'{"label":"…"}'}
                      ]
        }
    """
    template_str: str = prompt['template']
    latex_key = 'latex'

    split_marker = '### LaTeX:'
    if split_marker not in template_str:
        raise ValueError(f"Cannot find '{split_marker}' in prompt['template']")

    before, after = template_str.split(split_marker, maxsplit=1)
    system_text = before.strip()

    user_template = split_marker + after
    user_text = user_template.format(latex=sample[latex_key]).strip()

    assistant_json = json.dumps({'label': sample['label']})

    return {
        'messages': [
            {'role': 'system', 'content': system_text},
            {'role': 'user', 'content': user_text},
            {'role': 'assistant', 'content': assistant_json},
        ]
    }


def formatting_func(tokenizer: LlamaTokenizerFast, batch: dict[str, Any]) -> dict[str, Any]:
    """
    Expects batch['messages'] as a list of lists of dicts:
    [
        [
            {'role': 'system', 'content': ...},
            {'role':'user', 'content': ...},
            {'role': 'assistant', 'content':...},
        ],
    ]
    Returns a dict with 'input_ids', 'attention_mask', and 'labels'.
    """
    input_strs: list[str] = []

    for messages in batch['messages']:
        full_prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False,
        )
        input_strs.append(full_prompt)

    tokenized = tokenizer(input_strs, truncation=True, max_length=512, padding='max_length')
    tokenized['labels'] = tokenized['input_ids'].copy()

    return tokenized
