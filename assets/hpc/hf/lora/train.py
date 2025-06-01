# train.py

import json

from logging import INFO, basicConfig, getLogger
from pathlib import Path
from typing import cast

import huggingface_hub
import numpy as np
import torch
import wandb

from datasets import DatasetDict, load_dataset
from datasets.download import DownloadConfig
from decouple import config
from optuna import Trial
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from sklearn.metrics import f1_score
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

from .llama_3_1_8b import (
    format_prompt,
    formatting_func,
    init_language_model,
    init_tokenizer,
)


# huggingface
HF_USERNAME = config('HF_USERNAME', default=None)
HF_TOKEN = config('HF_TOKEN', default=None)

# weights and biases
WANDB_PROJECT = config('WANDB_PROJECT', default=None)
WANDB_API_KEY = config('WANDB_API_KEY', default=None)

# paths
HF_HOME = Path(...)


# TODO set HF_HOME=... and bind it
MODEL_NAME = ...
DATASET_NAME = ...


basicConfig(level=INFO, format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s')
logger = getLogger(__name__)


def compute_metrics(
    eval_preds: tuple[np.ndarray | torch.Tensor, np.ndarray | torch.Tensor],
) -> dict[str, float]:
    """
    Compute F1 for either binary or multiclass classification.
    eval_preds is a tuple (logits, labels) coming from SFTTrainer.evaluate().
    """
    logits, labels = eval_preds

    # Ensure logits is a Tensor
    if not isinstance(logits, torch.Tensor):
        logits = torch.tensor(logits)

    preds = logits.argmax(dim=-1).cpu().numpy()

    # Ensure labels is a Tensor
    if not isinstance(labels, torch.Tensor):
        labels = torch.tensor(labels)

    labels = labels.cpu().numpy()

    # Determine if binary or multiclass
    unique_labels = set(labels.flatten().tolist())
    f1 = f1_score(
        labels.flatten(),
        preds.flatten(),
        average='binary' if len(unique_labels) == 2 else 'weighted',
    )

    return {'f1': f1}


class GracefulStopCallback(TrainerCallback):
    def on_step_end(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs,
    ):
        return control


def main(trial: Trial):
    # initialization
    huggingface_hub.login(token=HF_TOKEN)
    wandb.login(key=WANDB_API_KEY)
    wandb.init(
        project=WANDB_PROJECT,
        name=f'{MODEL_NAME}_{trial.study._study_id}_{trial._trial_id}_qlora',
    )

    tokenizer = AutoTokenizer.from_pretrained(
        pretrained_model_name_or_path=MODEL_NAME,
        use_fast=True,
        trust_remote_code=True,
    )
    tokenizer = cast(PreTrainedTokenizerBase, tokenizer)
    init_tokenizer(tokenizer)

    repo_id = f'{HF_USERNAME}/{DATASET_NAME}'

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
        lambda x: format_prompt(x, prompt), remove_columns=dataset_dict['train'].column_names
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
        pretrained_model_name_or_path=MODEL_NAME,
        trust_remote_code=True,
        quantization_config=bits_and_bytes_config,
        device_map='auto',
    )
    model = cast(PreTrainedModel, model)
    init_language_model(model)

    r = trial.suggest_int('r', 4, 32, step=1)
    lora_alpha = trial.suggest_int('lora_alpha', 8, 64, step=8)
    lora_dropout = trial.suggest_float('lora_dropout', 0.0, 0.3, step=0.05)

    peft_config = LoraConfig(
        r=r,
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
        target_modules=...,  # NOTE depends on model
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
        output_dir=f'out/trainer/{trial._trial_id}',
        do_train=True,
        do_eval=True,
        do_predict=False,
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

    wandb_callback = WandbCallback(
        wandb_kwargs={
            'name': f'lora-optuna-run-{trial.number}',
            'tags': [
                f'r={r}',
                f'alpha={lora_alpha}',
                f'dropout={lora_dropout}',
            ],
            'notes': f'Optuna trial #{trial.number} with params {trial.params}',
        }
    )

    data_collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)

    trainer = SFTTrainer(
        model=model,
        args=sft_config,
        data_collator=data_collator,
        train_dataset=train_dataset,
        eval_dataset=validate_dataset,
        test_dataset=test_dataset,
        processing_class=tokenizer,
        callbacks=[wandb_callback],
        optimizer_cls_and_kwargs=(AdamW, {'lr': 2e-4, 'weight_decay': 0.01}),
        preprocess_logits_for_metrics=False,
        compute_metrics=compute_metrics,
        formatting_func=lambda batch: formatting_func(tokenizer, batch),
    )

    trainer.train(
        resume_from_checkpoint=True,
        trial=trial,
        ignore_keys_for_eval=['past_key_values', 'hidden_states', 'attentions'],
    )
    trainer.model.save_pretrained(
        save_directory=f'out/trainer/model/{trial._trial_id}',
        push_to_hub=False,
        token=None,
        save_peft_format=True,
    )
    eval_results = trainer.evaluate(eval_dataset=validate_dataset)
    f1 = eval_results['eval_f1']

    return f1


if __name__ == '__main__':
    main()
