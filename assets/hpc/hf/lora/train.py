import json

from logging import INFO, basicConfig, getLogger
from pathlib import Path
from typing import cast

import huggingface_hub
import wandb

from datasets import DatasetDict, load_dataset
from datasets.download import DownloadConfig
from decouple import config
from optuna import Trial
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from torch.optim import AdamW
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    DataCollatorForLanguageModeling,
    PreTrainedModel,
    PreTrainedTokenizerBase,
    TrainerCallback,
    TrainerControl,
    TrainerState,
    TrainingArguments,
)
from transformers.integrations import WandbCallback
from trl import SFTConfig, SFTTrainer

from .llama import init_llama_language_model, init_llama_tokenizer


# huggingface
HF_USERNAME = config('HF_USERNAME', default=None)
HF_TOKEN = config('HF_TOKEN', default=None)

# weights and biases
WANDB_PROJECT = config('WANDB_PROJECT', default=None)
WANDB_API_KEY = config('WANDB_API_KEY', default=None)

# models
MODEL_NAME = config('MODEL_NAME', default=None)
TOKENIZER_NAME = config('TOKENIZER_NAME', default=None)

# dataset
DATASET_PATH = config('DATASET_PATH', default=None)

# paths
CACHE_DIR_PATH = Path('data')

# TODO set HF_HOME=... and bind it


basicConfig(
    level=INFO, format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s'
)
logger = getLogger(__name__)


class GracefulStopCallback(TrainerCallback):
    def on_step_end(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs,
    ):
        # TODO
        return control


def format_prompt(sample: dict[str, str], prompt: dict):
    template: str = prompt['template']
    input_keys: list[str] = prompt['input_keys']

    return {
        'text': template.format(**{key: sample[key] for key in input_keys}),
        'label': sample['label'],
    }


def main(trial: Trial, resume: bool, dataset_name: str):
    # initialization
    huggingface_hub.login(token=HF_TOKEN)
    wandb.login(key=WANDB_API_KEY)
    wandb.init(project=WANDB_PROJECT, name='TinyLlama-1.1B-qlora')

    tokenizer = AutoTokenizer.from_pretrained(
        pretrained_model_name_or_path=...,
        use_fast=True,
        trust_remote_code=True,
    )
    tokenizer = cast(PreTrainedTokenizerBase, tokenizer)
    init_llama_tokenizer(tokenizer)

    repo_id = f'{HF_USERNAME}/{dataset_name}'

    download_config = DownloadConfig(
        max_retries=3,
        disable_tqdm=True,
    )
    dataset_dict: DatasetDict = load_dataset(
        path=repo_id,
        split=None,
        download_config=download_config,
        token=HF_TOKEN,
        trust_remote_code=True,
    )
    prompt_json_path = huggingface_hub.hf_hub_download(
        repo_id=repo_id,
        filename='prompt.json',
        repo_type='dataset',
        token=HF_TOKEN,
    )
    prompt_json_bytes = Path(prompt_json_path).read_bytes()
    prompt = json.loads(prompt_json_bytes)

    dataset_dict = dataset_dict.map(
        lambda x: format_prompt(x, prompt), remove_columns=['id']
    )

    train_dataset = dataset_dict['train']
    validate_dataset = dataset_dict['validate']
    test_dataset = dataset_dict['test']

    bits_and_bytes_config = BitsAndBytesConfig(
        load_in_8bit=True,
        llm_int8_threshold=6.0,
        llm_int8_enable_fp32_cpu_offload=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        pretrained_model_name_or_path=...,
        trust_remote_code=True,
        quantization_config=bits_and_bytes_config,
        device_map='auto',
    )
    model = cast(PreTrainedModel, model)
    init_llama_language_model(model)

    peft_config = LoraConfig(
        r=16,
        lora_alpha=16,
        lora_dropout=0.05,
        target_modules=['q_proj', 'k_proj', 'v_proj'],  # TODO depends on model
        use_dora=True,
    )

    model = prepare_model_for_kbit_training(
        model=model,
        use_gradient_checkpointing=True,
    )

    model = get_peft_model(
        model=model,
        peft_config=peft_config,
        adapter_name='default',
        mixed=False,
    )

    sft_config = SFTConfig(
        output_dir=...,  # TODO
        do_train=True,
        do_eval=True,
        do_predict=True,
        eval_strategy='steps',
        eval_steps=100,
        save_strategy='steps',
        save_steps=100,
        save_total_limit=2,
        disable_tqdm=True,
        per_device_train_batch_size=8,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        num_train_epochs=3,
        fp16=True,
        weight_decay=0.01,
        report_to='wandb',
        logging_strategy='steps',
        logging_steps=100,
        logging_first_step=True,
    )

    wandb_callback = WandbCallback(  # TODO use better kwargs
        wandb_kwargs={
            'name': 'lora-run',
            'tags': ['experiment-1'],
            'notes': 'testing 2e-4 lr',
        }
    )
    data_collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)
    optimizer_cls_and_kwargs = (
        AdamW,
        {'lr': 2e-4, 'weight_decay': 0.01},
    )

    trainer = SFTTrainer(
        model=model,
        args=sft_config,
        data_collator=data_collator,
        train_dataset=train_dataset,
        eval_dataset=validate_dataset,
        test_dataset=test_dataset,
        processing_class=tokenizer,
        callbacks=[wandb_callback],
        optimizer_cls_and_kwargs=optimizer_cls_and_kwargs,
        preprocess_logits_for_metrics=...,  # TODO
        formatting_func=...,  # TODO
    )

    trainer.train(
        resume_from_checkpoint=resume,
        trial=trial,
        ignore_keys_for_eval=['past_key_values', 'hidden_states', 'attentions'],
    )

    trainer.model.save_pretrained(
        save_directory=...,  # TODO bind
        push_to_hub=False,
        token=None,
        save_peft_format=True,
    )


if __name__ == '__main__':
    main()
